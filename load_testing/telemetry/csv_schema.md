# `resource_usage.csv` schema

| column | type | description |
|---|---|---|
| timestamp_utc | RFC3339 string | UTC sample timestamp |
| pid | int | sampled process PID |
| cpu_percent | float | process cpu percent from psutil |
| rss_bytes | int | resident memory bytes |
| vms_bytes | int | virtual memory bytes |
| threads | int | process thread count |
| open_fds | int/empty | open fd count (empty when unsupported) |
| read_bytes_total | int/empty | process cumulative read bytes |
| write_bytes_total | int/empty | process cumulative write bytes |
| system_cpu_percent | float/empty | host CPU percent |
| system_mem_percent | float/empty | host memory percent |

Unsupported metrics are emitted as empty CSV fields for cross-platform compatibility.
