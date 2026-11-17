import socket
import json
import threading
import time

# Define the network ports for your four antennas
# (e.g., matching Northwest, Northeast, Southeast, Southwest arrays)
ANTENNA_PORTS = {
    12341: "Northwest",
    12342: "Northeast",
    12343: "Southeast",
    12344: "Southwest"
}

# Thread-safe global ledger: { mac_address: [(sample_num, timestamp, antenna_direction, rssi)] }
packet_ledger = {}
ledger_lock = threading.Lock()  # Prevents corruption when threads write at the same time

LOOP_DURATION = 0.020  # 20 milliseconds array loop threshold

def analyze_packet_collision(transmitter_mac, current_sample, timestamp_float, direction, rssi_val):
    """Thread-safe comparison matrix to mark 20ms multi-antenna hits."""
    with ledger_lock:
        if transmitter_mac not in packet_ledger:
            packet_ledger[transmitter_mac] = []
        else:
            # Check history for collisions inside this 20ms full-array rotation loop
            for prev_sample, prev_time, prev_direction, prev_rssi in packet_ledger[transmitter_mac]:
                time_delta = abs(timestamp_float - prev_time)
                
                if time_delta <= LOOP_DURATION and direction != prev_direction:
                    print(f"\n[LOOP HIT] MAC {transmitter_mac} captured across sectors within 20ms!")
                    print(f"  -> Sector A: {prev_direction:10} | RSSI: {prev_rssi:.2f} dBm (Sample {prev_sample})")
                    print(f"  -> Sector B: {direction:10} | RSSI: {rssi_val:.2f} dBm (Sample {current_sample})")
                    print(f"  -> Rotation Delta: {time_delta * 1000:.2f} ms")
                    
                    if rssi_val > prev_rssi:
                        print(f"  [*] Signal peak shifting toward the {direction} sector.")
                    else:
                        print(f"  [*] Signal peak remains dominant in the {prev_direction} sector.")

        # Log current capture
        packet_ledger[transmitter_mac].append((current_sample, timestamp_float, direction, rssi_val))
        
        # Performance cleanup: Flush tracking history older than 20ms
        packet_ledger[transmitter_mac] = [
            item for item in packet_ledger[transmitter_mac] if (timestamp_float - item[1]) <= LOOP_DURATION
        ]

def udp_listener_worker(port, direction):
    """Dedicated background worker thread for an individual antenna port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))
    print(f"[ONLINE] Dedicated listener active on Port {port} for {direction} Array.")
    
    while True:
        try:
            data, addr = sock.recvfrom(65535)
            packet_payload = json.loads(data.decode('utf-8'))
            
            tag_contents = packet_payload["metadata"]
            frame_bytes = bytes(packet_payload["payload"])
            
            # Slice transmitter MAC address safely from index 10 onwards
            if len(frame_bytes) >= 16:
                mac_bytes = frame_bytes[10:16]
                transmitter_mac = ":".join(f"{b:02x}" for b in mac_bytes)
            else:
                continue
            
            # Pull metrics from tags
            current_sample = tag_contents.get("sample_number", 0)
            current_time = tag_contents.get("rx_time", [0, 0.0])
            rssi_val = float(tag_contents.get("rssi", -100.0))
            
            timestamp_float = float(current_time[0]) + float(current_time[1])
            
            # Send to the central processing matrix
            analyze_packet_collision(transmitter_mac, current_sample, timestamp_float, direction, rssi_val)
            
        except Exception as e:
            print(f"Error on Port {port} ({direction}): {e}")

# Main execution loop initializing the thread pool
if __name__ == "__main__":
    print("Starting Multi-Port Spatial Tracking Server...")
    threads = []
    
    # Spin up one thread per antenna network socket
    for port, direction in ANTENNA_PORTS.items():
        t = threading.Thread(target=udp_listener_worker, args=(port, direction), daemon=True)
        threads.append(t)
        t.start()
        
    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Directional Server.")

