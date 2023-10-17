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

    def check_version(self, rhost, rport, ssl):
        url = self.generate_url(rhost, rport, ssl, "/webui/logoutconfirm.html?logon_hash=1")
        try:
            response = requests.post(url)
            pattern = re.compile(r'^([a-f0-9]{18})\s*$')
            res = pattern.findall(response.text)
            if res:
                print(f"Found implant-id: {res[0]}, rhost: {rhost}, rport: {rport}, ssl: {ssl}")
                return "Vulnerable"
            return "NotVulnerable"
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
    parser.add_argument("--rhost", required=True, help="Remote host to target")
    parser.add_argument("--rport", type=int, default=80, help="Remote port (default: 80)")
    parser.add_argument("--ssl", action="store_true", help="Use SSL (default: False)")

    args = parser.parse_args()

    sploit = XEImplantScanner()
    sploit.validate_target(args.rhost, args.rport, args.ssl)
    sploit.check_version(args.rhost, args.rport, args.ssl)
    sploit.run_exploit(None) 
