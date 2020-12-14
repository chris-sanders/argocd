#!/bin/env python3
"""Command line test helpers"""
import datetime
import subprocess
import tempfile
import time
from pathlib import Path

import pexpect
import yaml

from kubernetes import client, config


class TimeoutException(Exception):
    pass


class NotFound(Exception):
    pass


class Kubernetes:
    """Kubernetes api wrapper"""

    def __init__(self):
        """Initialize the api"""

        _, current_context = config.list_kube_config_contexts()
        config.load_kube_config(context=current_context["name"], persist_config=False)
        self.core_v1_api = client.CoreV1Api()

    def create_namespace(self, namespace):
        """Create a namespace"""

        metadata = client.V1ObjectMeta(name=namespace)
        namespace = client.V1Namespace(metadata=metadata)
        api_response = self.core_v1_api.create_namespace(namespace)

        return api_response

    def get_service_cluster_ip(self, namespace, name):
        """Get an IP for a service by name"""
        service_list = self.core_v1_api.list_namespaced_service(namespace)

        if not service_list.items:
            raise NotFound(f"No services in namespace {namespace}")

        for service in service_list.items:
            if service.metadata.name == name:
                return service.spec.cluster_ip

        raise NotFound(f"cluster_ip not found for {name} in {namespace}")

    def get_pod_by_label(self, namespace, label):
        """Get a pod by lable"""
        pod_list = self.core_v1_api.list_namespaced_pod(namespace, label_selector=label)

        if not pod_list.items:
            raise NotFound(f"No pods in namespace {namespace} with label {label}")

        return pod_list.items

    def all_containers_ready(self, namespace, label=None):
        """Check if all containers in all pods are ready"""

        ready = True

        if label:
            pods = self.core_v1_api.list_namespaced_pod(namespace, label_selector=label)
        else:
            pods = self.core_v1_api.list_namespaced_pod(namespace)

        if not len(pods.items):
            return False

        for pod in pods.items:
            try:
                for container in pod.status.container_statuses:
                    ready = ready & container.ready
            except TypeError:
                return False

        return ready

    def wait_containers_ready(self, namespace, label=None, timeout=120):
        """Wait up to timeout for all containers to be ready."""
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=timeout)

        while True:
            if self.all_containers_ready(namespace, label):
                return
            elif datetime.datetime.now() > end:
                raise TimeoutException(
                    f"Timed out waiting for containers in {namespace}"
                )
            else:
                time.sleep(0.5)

    def get_pod_logs(self, namespace=None, label=None):
        if namespace:
            if label:
                pods = self.core_v1_api.list_namespaced_pod(
                    namespace, label_selector=label
                )
            else:
                pods = self.core_v1_api.list_namespaced_pod(namespace)
        else:
            if label:
                pods = self.core_v1_api.list_pod_for_all_namespaces(
                    label_selector=label
                )
            else:
                pods = self.core_v1_api.list_pod_for_all_namespaces()

        # if not len(pods.items):
        #     return False

        for pod in pods.items:
            data = {}
            namespace = pod.metadata.namespace
            pod_name = pod.metadata.name
            data["pod"] = pod_name

            for container in pod.spec.containers:
                container = container.name
                data["container"] = container
                try:
                    data["log"] = self.core_v1_api.read_namespaced_pod_log(
                        name=pod_name, namespace=namespace, container=data["container"],
                    )
                except client.exceptions.ApiException as e:
                    data["log"] = print(e)
                yield data


class Kubectl:
    """Kubectl cli wrapper"""

    def create_namespace(self, namespace, timeout=30):
        """Create a namespaces"""
        cmd = ["kubectl", "create", "namespace", namespace]

        return subprocess.run(cmd, timeout=timeout, check=True, shell=False, text=True)

    def get_pods(self, namespace=None, timeout=30):
        cmd = [
            "kubectl",
            "get",
            "po",
        ]

        if namespace:
            cmd.append(f"-n {namespace}")
        else:
            cmd.append("-A")

        return subprocess.run(cmd, timeout=timeout, check=True, shell=False, text=True)

    def apply(self, file, sync=False, timeout=10):
        """Apply an application and disable autosync"""
        with tempfile.NamedTemporaryFile(mode="w") as tmp_app:
            with open(file, "r") as app:
                contents = yaml.safe_load(app)

            if not sync:
                try:
                    del contents["spec"]["syncPolicy"]["automated"]
                except KeyError:
                    pass
            yaml.dump(contents, tmp_app)
            cmd = [
                "kubectl",
                "apply",
                "-f",
                f"{tmp_app.name}",
            ]

            return subprocess.run(
                cmd,
                timeout=timeout,
                check=True,
                shell=False,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.STDOUT,
                text=True,
            )


class Helm:
    """Helm cli wrapper"""

    def list(self):
        cmd = ["helm", "list"]
        cp = subprocess.run(
            cmd,
            check=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True,
        )
        print(cp.stdout)
        print(cp.args)

    def install(
        self,
        path: Path,
        namespace: str,
        name: str,
        values: list = [],
        timeout: int = 30,
    ) -> subprocess.CompletedProcess:
        cmd = [
            "helm",
            "install",
            f"{name}",
            f"{path}",
            "-n",
            f"{namespace}",
        ]

        for value in values:
            file_path = path / value
            cmd.extend(["-f", f"{file_path.resolve()}"])

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            text=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
        )

    def update(self, path: Path, timeout: int = 30):
        cmd = ["helm", "dependencies", "update", f"{path}"]

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            text=True,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
        )


class Argo:
    """Argo cli wrapper"""

    def __init__(self, path="./argocd/", values=["values.yaml"]):
        self.cfg_file = tempfile.NamedTemporaryFile(delete=False)
        self.helm = Helm()
        self.kubernetes = Kubernetes()
        self.argo_path = Path(path)
        self.values = values

    def install(self):
        """Install argo if it is not already installed"""
        existing = False
        try:
            self.kubernetes.create_namespace("argocd")
        except client.exceptions.ApiException as e:
            if e.status == 409:
                # Already exists, continue
                existing = True
            else:
                raise e

        if existing:
            self.kubernetes.wait_containers_ready("argocd")
        else:
            self.helm.update(path=self.argo_path)
            self.helm.install(
                path=self.argo_path,
                name="argocd",
                namespace="argocd",
                values=self.values,
            )
            self.kubernetes.wait_containers_ready("argocd")

    def login(self):
        """Login the cli"""
        self.server_ip = self.kubernetes.get_service_cluster_ip(
            "argocd", "argocd-server"
        )
        self.pod_name = self.kubernetes.get_pod_by_label(
            "argocd", "app.kubernetes.io/name=argocd-server"
        )[0].metadata.name
        prompt = pexpect.spawn(
            f"argocd login {self.server_ip}"
            f" --config {self.cfg_file.name}"
            f" --grpc-web"
            f" --insecure"
        )
        prompt.expect("Username:")
        prompt.sendline("admin")
        prompt.expect("Password:")
        prompt.sendline(self.pod_name)
        prompt.expect(pexpect.EOF)

    def list_apps(self, timeout=10):
        """Send a command to argocd"""
        cmd = ["argocd", "app", "list", "--config", f"{self.cfg_file.name}"]

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            shell=False,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True,
        )

    def disable_auto_sync(self, app, timeout=10):
        """Disable an apps autosync policy"""
        cmd = [
            "argocd",
            "app",
            "set",
            f"{app}",
            "--sync-policy",
            "none",
            "--config",
            f"{self.cfg_file.name}",
        ]

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            shell=False,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True,
        )

    def sync_app(self, app, path, timeout=120):
        """Sync an app"""
        cmd = [
            "argocd",
            "app",
            "sync",
            f"{app}",
            "--local",
            f"{path}",
            "--config",
            f"{self.cfg_file.name}",
        ]

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=True,
            shell=False,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True,
        )

    def delete(self, app, cascade=True, timeout=120):
        """Remove an application"""
        cmd = [
            "argocd",
            "app",
            "delete",
            f"{app}",
            "--cascade",
            f"{cascade}",
            "--config",
            f"{self.cfg_file.name}",
        ]

        return subprocess.run(
            cmd,
            timeout=timeout,
            check=False,
            shell=False,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            text=True,
        )

        # deadline = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        # while True:
        #     try:
        #         return subprocess.run(
        #             cmd,
        #             timeout=timeout,
        #             check=True,
        #             shell=False,
        #             # stdout=subprocess.PIPE,
        #             # stderr=subprocess.STDOUT,
        #             text=True,
        #         )
        #     except subprocess.CalledProcessError as err:
        #         if datetime.datetime.now() > deadline:
        #             raise err
