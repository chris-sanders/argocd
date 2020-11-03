#! /bin/env python3
from cli import Argo, Kubectl, Kubernetes


class TestBaseApp:
    def setup_class(cls):
        cls.kubernetes = Kubernetes()
        cls.kubectl = Kubectl()
        cls.argo = Argo()
        cls.argo.install()
        cls.argo.login()

    def test_base_install(self):
        """Test applying the app"""
        self.kubectl.apply("./apps/base/app/base-lab.yaml")
        self.argo.sync_app("base", "./apps/base/")
        self.kubernetes.wait_containers_ready("argocd")
        self.kubernetes.wait_containers_ready("metallb")
        self.kubernetes.wait_containers_ready("traefik")
