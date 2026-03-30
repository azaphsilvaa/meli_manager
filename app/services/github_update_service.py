import requests

from config.app_info import APP_VERSION, GITHUB_API_LATEST_RELEASE


class GitHubUpdateService:
    def get_current_version(self) -> str:
        return APP_VERSION

    def get_latest_release(self) -> dict | None:
        try:
            response = requests.get(
                GITHUB_API_LATEST_RELEASE,
                timeout=20,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "SOFTWARE-ML-Updater",
                },
            )

            if response.status_code != 200:
                print(f"Erro ao consultar release do GitHub: {response.status_code}")
                print(response.text)
                return None

            return response.json()

        except Exception as error:
            print(f"Erro ao consultar atualização no GitHub: {error}")
            return None

    def parse_release_data(self, release_data: dict) -> dict:
        tag_name = (release_data.get("tag_name") or "").strip()
        release_name = (release_data.get("name") or "").strip()
        html_url = (release_data.get("html_url") or "").strip()
        body = (release_data.get("body") or "").strip()

        assets = release_data.get("assets", []) or []

        download_url = html_url

        if assets:
            first_asset = assets[0]
            download_url = (first_asset.get("browser_download_url") or html_url).strip()

        normalized_latest = self.normalize_version(tag_name)

        return {
            "tag_name": tag_name,
            "release_name": release_name,
            "latest_version": normalized_latest,
            "download_url": download_url,
            "release_url": html_url,
            "notes": body,
        }

    def is_update_available(self, latest_version: str) -> bool:
        current_tuple = self.version_to_tuple(self.normalize_version(APP_VERSION))
        latest_tuple = self.version_to_tuple(self.normalize_version(latest_version))

        return latest_tuple > current_tuple

    def check_for_updates(self) -> dict:
        current_version = self.get_current_version()

        release_data = self.get_latest_release()

        if not release_data:
            return {
                "success": False,
                "current_version": current_version,
                "message": "Não foi possível consultar o GitHub.",
            }

        parsed = self.parse_release_data(release_data)
        latest_version = parsed["latest_version"]

        update_available = self.is_update_available(latest_version)

        return {
            "success": True,
            "current_version": current_version,
            "latest_version": latest_version,
            "update_available": update_available,
            "download_url": parsed["download_url"],
            "release_url": parsed["release_url"],
            "release_name": parsed["release_name"],
            "notes": parsed["notes"],
            "tag_name": parsed["tag_name"],
        }

    def normalize_version(self, version: str) -> str:
        version = version.strip()

        if version.lower().startswith("v"):
            version = version[1:]

        return version

    def version_to_tuple(self, version: str) -> tuple:
        parts = version.split(".")
        normalized_parts = []

        for part in parts:
            try:
                normalized_parts.append(int(part))
            except ValueError:
                normalized_parts.append(0)

        while len(normalized_parts) < 3:
            normalized_parts.append(0)

        return tuple(normalized_parts[:3])