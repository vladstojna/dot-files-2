# process the parsed config into useful parameters for Vagrant
# returns a hash with which maps the type (manager, replica, client) to
# a node or an array of nodes with hostname, cpus, memory and ip address parameters

IPV4_PREFIX = "192.168.56"

def process_config(cfg)
  add_element = -> (key:, hostname: key, address:) {
    retval = {}
    retval[:hostname] = hostname
    retval[:cpus] = cfg[key]["cpus"]
    retval[:memory] = cfg[key]["memory"]
    retval[:ip] = "#{address}"
    return retval
  }

  hash = {}
  hash[:manager] = add_element.call(key: "manager", address: "#{IPV4_PREFIX}.20")
  nodes = hash[:replica] = []
  (1..cfg["replica"]["count"]).each do |i|
    nodes.append(
      add_element.call(
        key: "replica",
        hostname: "#{cfg["replica"]["hostname"]}#{i}",
        address: "#{IPV4_PREFIX}.#{30 + i}"))
  end
  nodes = hash[:client] = []
  (1..cfg["client"]["count"]).each do |i|
    nodes.append(
      add_element.call(
        key: "client",
        hostname: "#{cfg["client"]["hostname"]}#{i}",
        address: "#{IPV4_PREFIX}.#{100 + i}"))
  end
  return hash
end
