import math

def get_class(first_octet):
    if 0 <= first_octet <= 127:
        return 'A'
    elif first_octet <= 191:
        return 'B'
    elif first_octet <= 223:
        return 'C'
    elif first_octet <= 239:
        return 'D'
    elif first_octet <= 255:
        return 'E'

def get_address(ip_str):
    addr = list(map(int, ip_str.split('.')))
    return addr

def get_net_mask(net_class):
    if net_class == 'A':
        return "255.0.0.0"
    elif net_class == 'B':
        return "255.255.0.0"
    elif net_class == 'C':
        return "255.255.255.0"
    else:
        return "N/A"

def get_default_ip_count(net_class):
    if net_class == 'A':
        return pow(2, 24)
    elif net_class == 'B':
        return pow(2, 16)
    elif net_class == 'C':
        return 256
    else:
        return 0

def print_subnet_info(addr, total_ips, subnets):
    ips_per_subnet = total_ips // subnets
    usable_ips_per_subnet = ips_per_subnet - 2

    print(f"Total IP addresses per subnet: {ips_per_subnet}")
    print(f"Usable IP addresses per subnet: {usable_ips_per_subnet}")

    for i in range(subnets):
        subnet_start = i * ips_per_subnet
        subnet_end = subnet_start + ips_per_subnet - 1

        subnet_addr = addr.copy()
        broadcast_addr = addr.copy()

        if total_ips == 256:  # Class C
            subnet_addr[3] = subnet_start
            broadcast_addr[3] = subnet_end
        elif total_ips == pow(2, 16):  # Class B
            subnet_addr[2] = subnet_start // 256
            subnet_addr[3] = subnet_start % 256
            broadcast_addr[2] = subnet_end // 256
            broadcast_addr[3] = subnet_end % 256
        elif total_ips == pow(2, 24):  # Class A
            subnet_addr[1] = subnet_start // (256 * 256)
            subnet_addr[2] = (subnet_start // 256) % 256
            subnet_addr[3] = subnet_start % 256
            broadcast_addr[1] = subnet_end // (256 * 256)
            broadcast_addr[2] = (subnet_end // 256) % 256
            broadcast_addr[3] = subnet_end % 256

        print(f"\nSubnet {i+1} Address: {'.'.join(map(str, subnet_addr))}")
        print(f"Broadcast Address: {'.'.join(map(str, broadcast_addr))}")
        print(f"Range of usable IPs: {subnet_addr[0]}.{subnet_addr[1]}.{subnet_addr[2]}.{subnet_addr[3] + 1} - {broadcast_addr[0]}.{broadcast_addr[1]}.{broadcast_addr[2]}.{broadcast_addr[3] - 1}")

def calculate_subnet_mask(net_class, subnets):
    borrowed_bits = math.ceil(math.log2(subnets))  # Number of bits to borrow

    if net_class == 'A':
        total_host_bits = 24
    elif net_class == 'B':
        total_host_bits = 16
    elif net_class == 'C':
        total_host_bits = 8
    else:
        return "N/A"

    remaining_host_bits = total_host_bits - borrowed_bits
    mask_bits = 32 - remaining_host_bits

    subnet_mask = []
    for i in range(4):
        if mask_bits >= 8:
            subnet_mask.append(255)
            mask_bits -= 8
        elif mask_bits > 0:
            subnet_mask.append(256 - pow(2, 8 - mask_bits))
            mask_bits = 0
        else:
            subnet_mask.append(0)

    return '.'.join(map(str, subnet_mask))

def main():
    ip_str = input("Enter the IPv4 address: ")
    addr = get_address(ip_str)
    net_class = get_class(addr[0])

    if net_class in ['D', 'E']:
        print(f"Class {net_class} is not suitable for subnetting.")
        return

    print(f"Class: {net_class}")
    print(f"Network ID: {addr[0]}.{addr[1]}.{addr[2]}")
    print(f"Default Subnet Mask: {get_net_mask(net_class)}")

    subnets = int(input("Enter the number of subnets: "))
    total_ips = get_default_ip_count(net_class)

    print_subnet_info(addr, total_ips, subnets)
    new_subnet_mask = calculate_subnet_mask(net_class, subnets)
    print(f"New Subnet Mask: {new_subnet_mask}")

if __name__ == "__main__":
    main()
