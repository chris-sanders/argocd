from pathlib import Path

from cli import Argo, Helm, Kubectl, Kubernetes


class TestArtifacts:
    def __init__(self):
        self.helm = Helm()
        self.kubernetes = Kubernetes()
        self.kubectl = Kubectl()
        self.argo = Argo()
        self.argo.install()
        self.argo.login()
        self.artifacts_dir = Path("./artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)

    def print_pods(self):
        self.kubectl.get_pods()

    def create_logs(self):
        for result in self.kubernetes.get_pod_logs():
            with open(
                self.artifacts_dir / f"{result['pod']}-{result['container']}.log", "w"
            ) as log_file:
                log_file.write(
                    f"Pod: {result['pod']}\n"
                    f"Container: {result['container']}\n"
                    f"Log: \n{result['log']}"
                )


if __name__ == "__main__":
    artifacts = TestArtifacts()
    artifacts.print_pods()
    artifacts.create_logs()
