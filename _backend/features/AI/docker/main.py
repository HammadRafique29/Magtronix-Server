import docker
import subprocess
from threading import Thread
from typing import List, Optional


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        Thread(target=self.start_docker_windows, daemon=True).start()


    def start_docker_windows(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(
                ["net", "start", "Docker Desktop Service"],
                shell=True,
                check=True,
                startupinfo=startupinfo
            )
        except subprocess.CalledProcessError as e: pass


    def list_images(self) -> List[str]:
        tags = [x.tags[0] for x in list(self.client.images.list()) if len(x.tags)>0]
        return tags
    

    def list_containers(self, all_containers: bool = False) -> List[str]:
        return [container.name for container in self.client.containers.list(all=all_containers)]


    def pull_image(self, image_name: str):
        response = self.client.api.pull(image_name, stream=True, decode=True)
        for line in response:
            status = line.get("status", "") 
            progress_detail = line.get("progressDetail", {})

            current = progress_detail.get("current", 0)
            total = progress_detail.get("total", 1)
            progress = round((current / total) * 100) if total > 1 else 0
            print(f"Status: {status} | Progress: {progress}%")

        print(f"\n✅ Image '{image_name}' pulled successfully!")


    def run_container(self, image_name: str, command: Optional[List[str]] = None, detach: bool = True):
        container = self.client.containers.run(image_name, command, detach=detach)
        print(f"Container {container.id} started successfully.")
        return container
    

    def remove_image(self, image_name: str):
        self.client.images.remove(image=image_name, force=True)
        print(f"Image {image_name} removed successfully.")


    def stop_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.stop()
        print(f"Container {container_id} stopped successfully.")


    def remove_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.remove(force=True)
        print(f"Container {container_id} removed successfully.")



if __name__ == "__main__":
    ds = DockerManager()
    ds.remove_container("6e9f43f0bfdd6e4b23540868ebb731a8ac6c55325c7f2cd76d700c9872478697")
    print(ds.list_containers())
    print(ds.list_images())

    # ds.pull_image("hello-world")