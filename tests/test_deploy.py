#! /bin/env python3
import os
from distutils.util import strtobool
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
        # Wait for BaseApp install
        cls.kubernetes.wait_containers_ready("metallb")
        cls.kubernetes.wait_containers_ready("traefik")

    def _check_clean(self, app):
        """Clean the application if requested"""
        clean_apps = bool(strtobool(os.environ.get("PYTEST_CLEAN_APPS", "false")))

        if clean_apps:
            self.argo.delete(app)

    def test_acme_dns_install(self):
        """Test applying the app"""
        self.kubectl.apply("./acme-dns/apps/acme-dns-lab.yaml")
        self.argo.sync_app("acmedns", "./acme-dns/")
        self.kubernetes.wait_containers_ready("acmedns")
        self._check_clean("acmedns")

    def test_bitwardenrs_install(self):
        """Test applying the app"""
        self.kubectl.apply("./bitwardenrs/apps/bitwardenrs-lab.yaml")
        self.argo.sync_app("bitwarden", "./bitwardenrs/")
        self.kubernetes.wait_containers_ready("bitwarden")
        self._check_clean("bitwarden")

    def test_cert_manager_install(self):
        """Test applying the app"""
        self.kubectl.apply("./cert-manager/apps/cert-manager-lab.yaml")
        self.argo.sync_app("cert-manager", "./cert-manager/")
        self.kubernetes.wait_containers_ready("cert-manager")
        self._check_clean("cert-manager")

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
        self._check_clean("gitlab")

    def test_goldilocks_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/goldilocks/apps/goldilocks-lab.yaml")
        self.argo.sync_app("goldilocks", "./llama/goldilocks/")
        self.kubernetes.wait_containers_ready(
            "llama", "app.kubernetes.io/name=goldilocks"
        )
        self._check_clean("goldilocks")

    def test_kps_install(self):
        """Test applying the app"""
        self.kubectl.apply("./llama/kube-prometheus-stack/apps/kps-lab.yaml", sync=True)
        # self.argo.sync_app("kube-prometheus-stack", "./llama/kube-prometheus-stack/")
        self.kubernetes.wait_containers_ready("llama", timeout=120)
        self._check_clean("kube-prometheus-stack")

    def test_minecraft_install(self):
        """Test applying the app"""
        self.kubectl.apply("./minecraft/apps/minecraft-lab.yaml")
        self.argo.sync_app("minecraft", "./minecraft/")
        self.kubernetes.wait_containers_ready("minecraft")
        self._check_clean("minecraft")

    def test_pihole_install(self):
        """Test applying the app"""
        self.kubectl.apply("./pihole/apps/pihole-lab.yaml")
        self.argo.sync_app("pihole", "./pihole/")
        self.kubernetes.wait_containers_ready("pihole")
        self._check_clean("pihole")

    def test_sealed_secrets_install(self):
        """Test applying the app"""
        self.kubectl.apply("./sealed-secrets/apps/sealed-secrets-lab.yaml")
        self.argo.sync_app("sealed-secrets-controller", "./sealed-secrets/")
        self.kubernetes.wait_containers_ready("sealed-secrets")
        self._check_clean("sealed-secrets-controller")

    def test_duplicati_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/duplicati/apps/duplicati-lab.yaml")
        self.argo.sync_app("duplicati", "./services/duplicati/")
        self.kubernetes.wait_containers_ready(
            "services", "app.kubernetes.io/name=duplicati"
        )
        self._check_clean("duplicati")

    def test_minio_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/minio/apps/minio-lab.yaml")
        self.argo.sync_app("minio", "./services/minio/")
        self.kubernetes.wait_containers_ready("services", "app=minio")
        self._check_clean("minio")

    def test_samba_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/samba/apps/samba-lab.yaml")
        self.argo.sync_app("samba", "./services/samba/")
        self.kubernetes.wait_containers_ready("services", "app=samba")
        self._check_clean("samba")

    def test_sftp_install(self):
        """Test applying the app"""
        self.kubectl.apply("./services/sftp/apps/sftp-lab.yaml")
        self.argo.sync_app("sftp", "./services/sftp/")
        self.kubernetes.wait_containers_ready("services", "app=sftp")
        self._check_clean("sftp")

    def test_unifi_install(self):
        """Test applying the app"""
        self.kubectl.apply("./unifi/apps/unifi-lab.yaml")
        self.argo.sync_app("unifi", "./unifi/")
        self.kubernetes.wait_containers_ready("unifi")
        self._check_clean("unifi")

    def test_nzbget_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/nzbget/apps/nzbget-lab.yaml")
        self.argo.sync_app("nzbget", "./usenet/nzbget/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=nzbget")
        self._check_clean("nzbget")

    def test_nzbhydra_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/nzbhydra/apps/nzbhydra-lab.yaml")
        self.argo.sync_app("nzbhydra", "./usenet/nzbhydra/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=nzbhydra2"
        )
        self._check_clean("nzbhydra")

    @pytest.mark.slow  # Not slow, but fails due to DNS on gh
    def test_organizr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/organizr/apps/organizr-lab.yaml")
        self.argo.sync_app("organizr", "./usenet/organizr/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=organizr"
        )
        self._check_clean("organizr")

    def test_plex_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/plex/apps/plex-lab.yaml")
        self.argo.sync_app("plex", "./usenet/plex/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=plex")
        self._check_clean("plex")

    def test_radarr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/radarr/apps/radarr-lab.yaml")
        self.argo.sync_app("radarr", "./usenet/radarr/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=radarr")
        self._check_clean("radarr")

    def test_sabnzbd_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/sabnzbd/apps/sabnzbd-lab.yaml")
        self.argo.sync_app("sabnzbd", "./usenet/sabnzbd/")
        self.kubernetes.wait_containers_ready(
            "usenet", "app.kubernetes.io/name=sabnzbd"
        )
        self._check_clean("sabnzbd")

    def test_sonarr_install(self):
        """Test applying the app"""
        self.kubectl.apply("./usenet/sonarr/apps/sonarr-lab.yaml")
        self.argo.sync_app("sonarr", "./usenet/sonarr/")
        self.kubernetes.wait_containers_ready("usenet", "app.kubernetes.io/name=sonarr")
        self._check_clean("sonarr")

    # def test_velero_install(self):
    #     """Test applying the app"""
    #     self.kubectl.apply("./velero/apps/velero-lab.yaml")
    #     self.argo.sync_app("velero", "./velero/")
    #     self.kubernetes.wait_containers_ready("velero")
