#! /bin/env python3
from cli import Argo


class TestArgo:
    def setup_class(cls):
        cls.argo = Argo()

    def test_argo_install(self):
        """Test that argo installs"""
        self.argo.install()

    def test_argo_reinstall(self):
        """Test initialize works with already installed argo"""
        self.argo.install()
