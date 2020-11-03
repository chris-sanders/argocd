#!/bin/env python3
from pathlib import Path

from cli import Helm, Kubernetes
# from pytest import fixture

# def test_install_argo():
#     """Test installing via helm."""
#     argo_path = Path("./argocd/")
#     values = ["values.yaml"]
#     kubernetes = Kubernetes()
#     api_response = kubernetes.create_namespace("argocd")
#     print(f"Api Create Response: {api_response}")
#     helm = Helm()
#     completed_process = helm.install(
#         path=argo_path, name="argocd", namespace="argocd", values=values
#     )
#     print(f"Helm install: {completed_process}")
#     assert kubernetes.wait_containers_ready("argocd")


# @fixture(scope='session')
def argocd():
    argo_path = Path("./argocd/")
    values = ["values.yaml"]
    kubernetes = Kubernetes()
    api_response = kubernetes.create_namespace("argocd")
    print(f"Api Create Response: {api_response}")
    helm = Helm()
    completed_process = helm.install(
        path=argo_path, name="argocd", namespace="argocd", values=values
    )
    print(f"Helm install: {completed_process}")
    assert kubernetes.wait_containers_ready("argocd")


# @fixture(autouse=True, scope='session')
def argo_cli(argocd):
    pass
