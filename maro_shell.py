import os
import subprocess


def run_cmd(cmd):
    # Sprawdzamy, czy potrzebujemy sudo (jeśli nie jesteśmy w grupie docker i nie jesteśmy rootem)
    try:
        # Próbujemy wykonać komendę. Jeśli docker wywali błąd uprawnień, dodajemy sudo.
        full_cmd = f"sudo {cmd}" if os.getuid() != 0 else cmd
        return subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except Exception as e:
        return f"Błąd: {str(e)}"

def show_status():
    print("\n--- [ STATUS USŁUGI ] ---")
    container = run_cmd(
        "docker ps --filter 'name=instagram_server' --format 'ID: {{.ID}} | Status: {{.Status}} | Porty: {{.Ports}}'")
    if not container:
        print("❌ Serwer NIE DZIAŁA (kontener stop)")
    else:
        print(f"✅ {container}")

    ip = run_cmd("docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' instagram_server")
    print(f"🌐 IP Kontenera: {ip if ip else 'Brak'}")
    print("-------------------------\n")


def main():
    print("=== MARO-SHELL v1.0 ===")
    print("Wpisz 'help' aby zobaczyć listę komend.")

    while True:
        try:
            cmd = input("maro > ").strip().lower()

            if cmd == "exit" or cmd == "quit":
                break
            elif cmd == "help":
                print("Dostępne komendy: show, logs, restart, stop, exit")
            elif cmd == "show":
                show_status()
            elif cmd == "logs":
                print(run_cmd("docker logs --tail 10 instagram_server"))
            elif cmd == "restart":
                print("Restartowanie...")
                os.system("make run")
            elif cmd == "stop":
                print("Zatrzymywanie...")
                os.system("make stop")
            elif cmd == "":
                continue
            else:
                print(f"Nieznana komenda: {cmd}")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()