#! /bin/env python3
from pathlib import Path
from cli import Argo, Helm, Kubectl, Kubernetes


class TestBaseApps:
    def setup_class(cls):
        cls.helm = Helm()
        cls.kubernetes = Kubernetes()
        cls.kubectl = Kubectl()
        cls.argo = Argo()
        cls.argo.install()
        cls.argo.login()

    def test_acme_dns_install(self):
        """Test applying the app"""
        self.kubectl.apply("./acme-dns/apps/acme-dns-lab.yaml")
        self.argo.sync_app("acmedns", "./acme-dns/")
        self.kubernetes.wait_containers_ready("acmedns")

    def test_bitwardenrs_install(self):
        """Test applying the app"""
        self.kubectl.apply("./bitwardenrs/apps/bitwardenrs-lab.yaml")
        self.argo.sync_app("bitwarden", "./bitwardenrs/")
        self.kubernetes.wait_containers_ready("bitwarden")

    def test_cert_manager_install(self):
        """Test applying the app"""
        self.kubectl.apply("./cert-manager/apps/cert-manager-lab.yaml")
        self.argo.sync_app("cert-manager", "./cert-manager/")
        self.kubernetes.wait_containers_ready("cert-manager")

    # def test_gitlab_install(self):
    #     """Test applying the app"""
    #     self.kubernetes.create_namespace("gitlab")
    #     self.helm.install(
    #         Path("./gitlab"), "gitlab", "gitlab", ["values.yaml", "values-lab.yaml"]
    #     )
    #     self.kubectl.apply("./gitlab/apps/gitlab-lab.yaml")
    #     # self.argo.sync_app("gitlab", "./gitlab/")
    #     self.kubernetes.wait_containers_ready("gitlab", timeout=900)

    def test_kps_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/kube-prometheus-stack/apps/kps-lab.yaml", sync=True)
        # self.argo.sync_app("kube-prometheus-stack", "./llama/kube-prometheus-stack/")
        self.kubernetes.wait_containers_ready("llama", timeout=120)

    def test_goldilocks_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/goldilocks/apps/goldilocks-lab.yaml")
        self.argo.sync_app("goldilocks", "./llama/goldilocks/")
        self.kubernetes.wait_containers_ready("llama")

    # def test_minecraft_install(self):
    #     """Test applying the app"""
    #     self.kubectl.apply("./minecraft/apps/minecraft-lab.yaml")
    #     self.argo.sync_app("minecraft", "./minecraft/")
    #     self.kubernetes.wait_containers_ready("minecraft")

    def test_pihole_install(self):
        """Test applying the app"""
        self.kubectl.apply("./pihole/apps/pihole-lab.yaml")
        self.argo.sync_app("pihole", "./pihole/")
        self.kubernetes.wait_containers_ready("pihole", timeout=100)

    def test_sealed_secrets_install(self):
        """Test applying the app"""
        self.kubectl.apply("./sealed-secrets/apps/sealed-secrets-lab.yaml")
        self.argo.sync_app("sealed-secrets-controller", "./sealed-secrets/")
        self.kubernetes.wait_containers_ready("sealed-secrets")
