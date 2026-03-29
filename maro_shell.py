import os
import subprocess
import base64
import requests
import time

# --- KOLORY ANSI ---
G = '\033[92m'  # Zielony
Y = '\033[93m'  # Żółty
R = '\033[91m'  # Czerwony
C = '\033[96m'  # Cyjan
N = '\033[0m'  # Reset

# --- KONFIGURACJA FLAGI ---
# CTF{pLmWnBqZtRcXySjK} zakodowane (Base64 + Shift 1)
SECRET_DATA = "RFVHe3FNeF5jUmRhWXVUZEt6S2xM"


def get_real_flag():
    try:
        decoded_bytes = base64.b64decode(SECRET_DATA)
        return "".join(chr(b - 1) for b in decoded_bytes)
    except:
        return "ERROR_FLAG"


def run_cmd(cmd):
    try:
        prefix = "sudo " if os.getuid() != 0 else ""
        return subprocess.check_output(f"{prefix}{cmd}", shell=True, stderr=subprocess.STDOUT).decode().strip()
    except:
        return ""


def debug_mode():
    print(f"\n{C}--- [ TRYB DEBUGOWANIA ] ---{N}")
    print(f"Dostępne: {G}send -r \"msg\"{N} (ruch), {G}send -f{N} (flaga), {R}exit{N}")

    while True:
        try:
            line = input(f"{C}(debug) > {N}").strip()
            if not line: continue

            if line == "exit":
                print(f"{Y}Wrócono do głównego menu.{N}")
                break

            if line.startswith("send"):
                parts = line.split(maxsplit=2)
                if len(parts) < 2:
                    print(f"{R}Użycie: send -r \"wiadomosc\" lub send -f{N}")
                    continue

                payload = ""
                u_agent = "Manual-Debug"

                if parts[1] == "-f":
                    payload = get_real_flag()
                    u_agent = "Debug-Flag-Trigger"
                    print(f"🚀 {G}Wysyłanie flagi do kontenera...{N}")
                elif parts[1] == "-r" and len(parts) > 2:
                    payload = parts[2].replace('"', '')
                    print(f"📡 {G}Wysyłanie szumu: {payload}{N}")

                try:
                    ip = run_cmd(
                        "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' instagram_server")
                    if not ip:
                        print(f"{R}❌ Błąd: Kontener nie działa!{N}")
                        continue

                    requests.post(
                        f"http://{ip}/internal_audit",
                        headers={'X-Flag-Vault': payload, 'User-Agent': u_agent},
                        data={'debug': 'true'},
                        timeout=2
                    )
                    print(f"{G}✅ Wysłano pomyślnie (sprawdź sniffer!).{N}")
                except Exception as e:
                    print(f"{R}❌ Błąd sieci: {e}{N}")

        except KeyboardInterrupt:
            break


def main():
    print(f"{Y}=== MARO-SHELL v1.3 [ULTIMATE EDITION] ==={N}")
    print("Wpisz 'help' aby zobaczyć listę komend.")

    while True:
        try:
            line = input(f"{G}maro > {N}").strip()
            if not line: continue

            parts = line.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ["exit", "quit"]:
                break

            elif cmd == "help":
                print(f"\n{C}Dostępne komendy:{N}")
                print(f"  {G}show{N}           - Status kontenera")
                print(f"  {G}debug{N}          - Tryb ręcznego wysyłania pakietów")
                print(f"  {G}logs{N}           - Ostatnie 10 linii logów")
                print(f"  {G}restart{N}        - Twardy restart laboratorium (make run)")
                print(f"  {G}check \"flaga\"{N}  - Weryfikacja zdobytej flagi")
                print(f"  {G}exit{N}           - Zamknij shella\n")

            elif cmd == "show":
                status = run_cmd(
                    "docker ps --filter 'name=instagram_server' --format 'ID: {{.ID}} | Status: {{.Status}}'")
                if status:
                    print(f"{G}✅ {status}{N}")
                else:
                    print(f"{R}❌ Serwer jest zatrzymany.{N}")

            elif cmd == "logs":
                print(run_cmd("docker logs --tail 10 instagram_server"))

            elif cmd == "restart":
                print(f"{Y}🔄 Restartowanie serwera...{N}")
                os.system("make run")

            elif cmd == "debug":
                debug_mode()

            elif cmd == "check":
                if arg.startswith('"') and arg.endswith('"'):
                    user_flag = arg[1:-1]
                    real_flag = get_real_flag()

                    if user_flag == real_flag:
                        print(f"\n{G}#################################################{N}")
                        print(f"{G}# [SUKCES] DOSTĘP PRZYZNANY!                    #{N}")
                        print(f"{G}# FLAGA: {real_flag}           #{N}")
                        print(f"{G}#################################################{N}")

                        print(f"\n{Y}⚡ Autozatrzymywanie serwera...{N}")
                        run_cmd("docker stop instagram_server")
                        print(f"{R}🔴 Serwer zatrzymany. Misja ukończona.{N}")

                        print(f"\n{C}Aby wyczyścić wszystko, wpisz w terminalu:{N}")
                        print(f"{G}make clean {N}\n")
                        break
                    else:
                        print(f"{R}❌ [BŁĄD] Nieprawidłowa flaga. Próbuj dalej!{N}")
                else:
                    print(f'{Y}⚠️  Format błędu! Użyj: check "TWOJA_FLAGA"{N}')

            else:
                print(f"{R}Nieznana komenda: {cmd}{N}")

        except KeyboardInterrupt:
            print("\nDo widzenia!")
            break


if __name__ == "__main__":
    main()