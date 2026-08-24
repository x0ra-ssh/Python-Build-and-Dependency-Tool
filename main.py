import asyncio
import ipaddress
import socket
import subprocess
import platform
import psutil
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Sparkline
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

COMMON_PORTS = [22, 80, 443, 445, 8080]

def get_wifi_interface_and_ip():
    """Detects active Wi-Fi interface and local IP address."""
    for iface, addrs in psutil.net_if_addrs().items():
        # Heuristic check for Wi-Fi interface names
        if any(w in iface.lower() for w in ["wi-fi", "wifi", "wlan", "en0"]):
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    return iface, addr.address
    # Fallback to default non-loopback IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return "Default Network", ip

async def async_ping(ip: str) -> bool:
    """Non-blocking ICMP ping probe."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout = "1000" if platform.system().lower() == "windows" else "1"
    cmd = ["ping", param, "1", "-w", timeout, ip]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    await proc.communicate()
    return proc.returncode == 0

async def check_port(ip: str, port: int) -> bool:
    """Non-blocking TCP port probe."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=0.3
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

class NetworkMapperApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 3fr;
        grid-columns: 1fr 2fr;
        background: #0d1117;
    }
    .box {
        border: heavy #58a6ff;
        padding: 1;
        margin: 1;
    }
    #stat-box {
        color: #58a6ff;
    }
    #graph-box {
        color: #3fb950;
    }
    #table-box {
        column-span: 2;
        border: heavy #bc8cff;
    }
    DataTable {
        height: 100%;
    }
    """
    
    BINDINGS = [("q", "quit", "Quit"), ("r", "scan", "Rescan Subnet")]
    
    # Reactive traffic stats for dynamic sparklines
    rx_bytes = reactive([])
    tx_bytes = reactive([])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="stat-box", classes="box"):
            yield Static("Detecting Network...", id="net-info")
            
        with Container(id="graph-box", classes="box"):
            yield Static("[b]Bandwidth Usage (Rx/Tx)[/b]")
            yield Sparkline(data=[0]*30, id="rx-spark")

        with Container(id="table-box", classes="box"):
            yield DataTable(id="host-table")
            
        yield Footer()

    def on_mount(self) -> None:
        self.iface, self.local_ip = get_wifi_interface_and_ip()
        self.subnet = str(ipaddress.ip_network(f"{self.local_ip}/24", strict=False))
        
        # Populate Info Box
        info_widget = self.query_one("#net-info", Static)
        info_widget.update(
            f"[b]Interface:[/b] {self.iface}\n"
            f"[b]Local IP:[/b] {self.local_ip}\n"
            f"[b]Subnet Target:[/b] {self.subnet}\n"
            f"[b]Status:[/b] Scanning..."
        )

        # Setup Table
        table = self.query_one("#host-table", DataTable)
        table.add_columns("Host IP", "Status", "Open Ports", "Latency Probe")

        # Initial metrics & scan initialization
        self.last_net = psutil.net_io_counters()
        self.set_interval(1.0, self.update_traffic_metrics)
        self.run_worker(self.scan_subnet, exclusive=True)

    def update_traffic_metrics(self) -> None:
        """Fetch network IO deltas and push to graph."""
        current_net = psutil.net_io_counters()
        rx_diff = (current_net.bytes_recv - self.last_net.bytes_recv) / 1024
        self.last_net = current_net
        
        sparkline = self.query_one("#rx-spark", Sparkline)
        new_data = list(sparkline.data)[1:] + [int(rx_diff)]
        sparkline.data = new_data

    async def scan_subnet(self) -> None:
        """Asynchronously scan the local subnet."""
        table = self.query_one("#host-table", DataTable)
        table.clear()
        
        network = ipaddress.ip_network(self.subnet, strict=False)
        tasks = [self.probe_host(str(ip)) for ip in network.hosts()]
        
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                ports_str = ", ".join(map(str, res["ports"])) if res["ports"] else "None"
                table.add_row(res["ip"], "[bold green]Online[/bold green]", ports_str, "OK")

    async def probe_host(self, ip: str):
        if await async_ping(ip):
            open_ports = []
            for port in COMMON_PORTS:
                if await check_port(ip, port):
                    open_ports.append(port)
            return {"ip": ip, "ports": open_ports}
        return None

    def action_scan(self) -> None:
        self.run_worker(self.scan_subnet, exclusive=True)

if __name__ == "__main__":
    app = NetworkMapperApp()
    app.run()