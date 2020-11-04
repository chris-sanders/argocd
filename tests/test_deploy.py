#! /bin/env python3
from pathlib import Path

import pytest
from cli import Argo, Helm, Kubectl, Kubernetes


class TestDeploy:
    def setup_class(cls):
        cls.helm = Helm()
        cls.kubernetes = Kubernetes()
        cls.kubectl = Kubectl()
        cls.argo = Argo()
        cls.argo.install()
        cls.argo.login()
        # Wait for base app install before running tests
        cls.kubernetes.wait_containers_ready("metallb")
        cls.kubernetes.wait_containers_ready("traefik")

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

    @pytest.mark.slow
    def test_gitlab_install(self):
        """Test applying the app"""
        self.kubernetes.create_namespace("gitlab")
        self.helm.install(
            Path("./gitlab"), "gitlab", "gitlab", ["values.yaml", "values-lab.yaml"]
        )
        self.kubectl.apply("./gitlab/apps/gitlab-lab.yaml")
        # self.argo.sync_app("gitlab", "./gitlab/")
        self.kubernetes.wait_containers_ready("gitlab", timeout=900)

    def test_goldilocks_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/goldilocks/apps/goldilocks-lab.yaml")
        self.argo.sync_app("goldilocks", "./llama/goldilocks/")
        self.kubernetes.wait_containers_ready(
            "llama", "app.kubernetes.io/name=goldilocks"
        )

    def test_kps_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/kube-prometheus-stack/apps/kps-lab.yaml", sync=True)
        # self.argo.sync_app("kube-prometheus-stack", "./llama/kube-prometheus-stack/")
        self.kubernetes.wait_containers_ready("llama", timeout=120)

    # def test_minecraft_install(self):
    #     """Test applying the app"""
    #     self.kubectl.apply("./minecraft/apps/minecraft-lab.yaml")
    #     self.argo.sync_app("minecraft", "./minecraft/")
    #     self.kubernetes.wait_containers_ready("minecraft")

    def test_pihole_install(self):
        """Test applying the app"""
        self.kubectl.apply("./pihole/apps/pihole-lab.yaml")
        self.argo.sync_app("pihole", "./pihole/")
        self.kubernetes.wait_containers_ready("pihole")

    def test_sealed_secrets_install(self):
        """Test applying the app"""
        self.kubectl.apply("./sealed-secrets/apps/sealed-secrets-lab.yaml")
        self.argo.sync_app("sealed-secrets-controller", "./sealed-secrets/")
        self.kubernetes.wait_containers_ready("sealed-secrets")

    def test_duplicati_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/duplicati/apps/duplicati-lab.yaml")
        self.argo.sync_app("duplicati", "./services/duplicati/")
        self.kubernetes.wait_containers_ready(
            "services", "app.kubernetes.io/name=duplicati"
        )

    def test_minio_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/minio/apps/minio-lab.yaml")
        self.argo.sync_app("minio", "./services/minio/")
        self.kubernetes.wait_containers_ready("services", "app=minio")

    def test_samba_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/samba/apps/samba-lab.yaml")
        self.argo.sync_app("samba", "./services/samba/")
        self.kubernetes.wait_containers_ready("services", "app=samba")

    def test_sftp_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/sftp/apps/sftp-lab.yaml")
        self.argo.sync_app("sftp", "./services/sftp/")
        self.kubernetes.wait_containers_ready("services", "app=sftp")

    def test_unifi_install(self):
        """Test applying the app"""
        self.kubectl.apply("./unifi/apps/unifi-lab.yaml")
        self.argo.sync_app("unifi", "./unifi/")
        self.kubernetes.wait_containers_ready("unifi")

    def test_nzbget_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/nzbget/apps/nzbget-lab.yaml")
        self.argo.sync_app("nzbget", "./usenet/nzbget/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=nzbget")

    def test_nzbhydra_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/nzbhydra/apps/nzbhydra-lab.yaml")
        self.argo.sync_app("nzbhydra", "./usenet/nzbhydra/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=nzbhydra2"
        )

    def test_organizr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/organizr/apps/organizr-lab.yaml")
        self.argo.sync_app("organizr", "./usenet/organizr/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=organizr"
        )

    def test_plex_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/plex/apps/plex-lab.yaml")
        self.argo.sync_app("plex", "./usenet/plex/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=plex")

    def test_radarr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/radarr/apps/radarr-lab.yaml")
        self.argo.sync_app("radarr", "./usenet/radarr/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=radarr")

    def test_sabnzbd_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/sabnzbd/apps/sabnzbd-lab.yaml")
        self.argo.sync_app("sabnzbd", "./usenet/sabnzbd/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=sabnzbd"
        )

    def test_sonarr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/sonarr/apps/sonarr-lab.yaml")
        self.argo.sync_app("sonarr", "./usenet/sonarr/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=sonarr")

    def test_velero_install(self):
        """Test applying the app"""
        self.kubectl.apply("./velero/apps/velero-lab.yaml")
        self.argo.sync_app("velero", "./velero/")
        self.kubernetes.wait_containers_ready("velero")
