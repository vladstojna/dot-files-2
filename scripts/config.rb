require "yaml"

def read_config(path)
  positive = -> (v) { return v > 0 }

  assert_config_block = -> (block, count_test = positive) {
    if block
      # if count does not exist, always return true
      valid_count = block["count"] ? count_test.call(block["count"]) : true
      block and
        block["hostname"] and
        positive.call(block["cpus"]) and
        positive.call(block["memory"]) and
        valid_count
    end
  }

  cfg = YAML.load(File.read(path))
  ["manager", "replica", "client"].each do |key|
    raise "Invalid block #{path}:#{key}" unless assert_config_block.call(cfg[key])
  end
  return cfg
end
