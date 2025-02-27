import requests
import re
import argparse


class XEScanner:
    def validate_target(self, rhost, rport, ssl):
        url = self.generate_url(rhost, rport, ssl, "/")
        try:
            response = requests.get(url)
            server = response.headers.get("Server")
            if not server or server.lower() != "nginx":
                print("Wrong or Missing Server")
                return False
            return "/webui" in response.text
        except:
            return False

    def check_menu_version(self, rhost, rport, ssl):
        url = self.generate_url(rhost, rport, ssl, "/webui/logoutconfirm.html?menu=1")
        try:
            response = requests.post(
                url, verify=False
            )  # The verify=False flag is equivalent to curl's -k flag
            if "2023" in response.text:
                print(
                    f"Compromised (menu version): rhost: {rhost}, rport: {rport}, ssl: {ssl}"
                )
                return "[!] Potentially Compromised"
            return "Not Compromised"
        except:
            return "Unknown"

    def check_version(self, rhost, rport, ssl):
        url = self.generate_url(
            rhost, rport, ssl, "/webui/logoutconfirm.html?logon_hash=1"
        )
        try:
            response = requests.post(url)
            pattern = re.compile(r"^([a-f0-9]{18})\s*$")
            res = pattern.findall(response.text)
            if res:
                print(
                    f"Found implant-id: {res[0]}, rhost: {rhost}, rport: {rport}, ssl: {ssl}"
                )
                return "[!] Potentially Compromised"
            return "Not Compromised"
        except:
            return "Unknown"

    def run_exploit(self, _):
        return True

    @staticmethod
    def generate_url(rhost, rport, ssl, path):
        if ssl:
            scheme = "https://"
        else:
            scheme = "http://"
        return f"{scheme}{rhost}:{rport}{path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XE Implant Scanner")
    parser.add_argument("--rhost", help="Single Remote host to target")
    parser.add_argument(
        "--rport", type=int, default=80, help="Remote port (default: 80)"
    )
    parser.add_argument("--ssl", action="store_true", help="Use SSL (default: False)")
    parser.add_argument(
        "--input_file", help="File containing list of IPs or domain names to scan"
    )

    args = parser.parse_args()

    sploit = XEScanner()

    if args.input_file:
        with open(args.input_file, "r") as file:
            for line in file:
                rhost = line.strip()
                if rhost:
                    print(f"Scanning {rhost}...")
                    sploit.validate_target(rhost, args.rport, args.ssl)
                    sploit.check_version(rhost, args.rport, args.ssl)
                    sploit.check_menu_version(rhost, args.rport, args.ssl)
    else:
        sploit.validate_target(args.rhost, args.rport, args.ssl)
        sploit.check_version(args.rhost, args.rport, args.ssl)
        sploit.check_menu_version(args.rhost, args.rport, args.ssl)
