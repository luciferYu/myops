#!/data/exec/python/bin/python3
# -*- coding:utf-8 -*-
# auth Yuzhiyi

import json
import os
import yaml
from pprint import pprint
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager

from ansible.playbook.play import Play
from ansible.playbook import Playbook
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


class MyResultCallback(ResultCallback):
    def __init__(self, shell_result):
        super(ResultCallback, self).__init__()
        self.shell_result = shell_result

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        #host = result._host
        #print(json.dumps({host.name: result._result}, indent=4))
        self.shell_result.append({result._host:result._result['stdout']})
        #print(result._result)


class AnsibleOperator(object):
    def __init__(self, hosts, forks=10, sources=['/etc/ansible/hosts']):  # 定义的主机文件, sources直接指定IP不可行
        # 用来加载解析yaml文件或JSON内容,并且支持vault的解密
        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')
        # self.results_callback = ResultCallback()
        self.shell_result = []
        self.results_callback = MyResultCallback(self.shell_result)
        self.Options = None
        self.options = None
        self.sources = sources
        with open(self.sources[0], 'w') as f:
            # yaml.dump(host_list, f)
            for host in hosts:
                f.write(host + '\n')
        self.inventory = InventoryManager(loader=self.loader, sources=sources)
        # 管理变量的类，包括主机，组，扩展等变量
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        # variable_manager.set_inventory(inventory)
        self.forks = forks

    def run_achoc(self, cmd, extra_vars={}):

        # play_source = {"name": "Ansible Ad-Hoc", "hosts": "10.121.74.231", "gather_facts": "no",
        #                "tasks": [{"action": {"module": "shell", "args": "ifconfig"}}]}
        # play_source = {"name": "Ansible Ad-Hoc", "hosts": "dev", "gather_facts": "no",
        #                "tasks": [{"action": {"module": "ping", "args": ""}}]}
        play_source = {"name": "Ansible Ad-Hoc", "hosts": "all", "gather_facts": "no",
                       "tasks": [{"action": {"module": "shell", "args": cmd}}]}

        self.Options = namedtuple('Options',
                                  ['connection',
                                   'module_path',
                                   'forks',
                                   'become',
                                   'become_method',
                                   'become_user',
                                   'check',
                                   'diff'])
        # connection参数，如果执行本地节点用'local', 远端节点用'smart'
        self.options = self.Options(connection='smart',
                                    module_path='/path/to/mymodules',
                                    forks=self.forks,
                                    become=None,
                                    become_method=None,
                                    become_user=None,
                                    check=False,
                                    diff=False)

        self.variable_manager.extra_vars = extra_vars

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        # actually run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.results_callback,
                # Use our custom callback instead of the ``default`` callback plugin
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def run_playbook(self, playbooks, extra_vars={}):
        self.Options = namedtuple('Options',
                                  ['connection',
                                   'forks',
                                   'become',
                                   'become_method',
                                   'become_user',
                                   'check',
                                   'listhosts',
                                   'listtasks',
                                   'listtags',
                                   'syntax',
                                   'module_path',
                                   'diff',
                                   'start_at_task',
                                   'private_key',
                                   ])
        self.options = self.Options(connection='smart',
                                    forks=self.forks,
                                    become=None,
                                    become_method=None,
                                    become_user=None,
                                    check=False,
                                    listhosts=False,
                                    listtasks=False,
                                    listtags=False,
                                    syntax=False,
                                    module_path="",
                                    diff=False,
                                    # start_at_task='install java package' )
                                    start_at_task='None',
                                    private_key='/root/.ssh/id_rsa')
        print(playbooks)
        print(extra_vars)
        print(self.inventory.get_hosts())
        self.variable_manager.extra_vars = extra_vars
        executor = PlaybookExecutor(playbooks, self.inventory, self.variable_manager, self.loader, self.options,
                                    self.passwords)
        result = executor.run()


if __name__ == '__main__':
    host_list = ['10.121.74.231', '10.221.73.74']
    ao = AnsibleOperator(host_list, forks=5)

    cmd = 'netstat -tlnp|grep hubb'

    ao.run_achoc(cmd)
    pprint(ao.results_callback.shell_result)




    #   运行playbook
    # 安装Nginx
    # playbook = os.path.join(os.path.dirname(__file__), 'deployment', 'ngx-server.yml')
    # extra_vars = {'ngx_version': 'nginx_1.10.1'}

    # 安装Node
    # playbook = os.path.join(os.path.dirname(__file__), 'deployment', 'node-server.yml')
    # extra_vars = {}

    # 安装Java
    # playbook = os.path.join(os.path.dirname(__file__), 'deployment', 'java-server.yml')
    # extra_vars = {'jdk_version': '8u91'}
    # #extra_vars = {'jdk_version': '7u79'}

    # 安装Python
    # playbook = os.path.join(os.path.dirname(__file__), 'deployment', 'py-server.yml')
    # extra_vars = {}
    #
    # 安装Hubble Agent
    playbook = os.path.join(os.path.dirname(__file__), 'deployment', 'hubble_agent.yml')
    extra_vars = {}
    #
    #
    playbooks = []
    playbooks.append(playbook)

    ao.run_playbook(playbooks, extra_vars=extra_vars)
