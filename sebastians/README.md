DNSr
===============

HotNets 2022: 16.Juni Deadline, 6 pages

Problem: (Large-scale) DNS scanning is fragile and unreliable?
-> Basis for other fast and large-scale scans, where DNS resolution is required (i.e. http, etc.)
-> Many resolvers employ rate limits or other filters to prevent abuse. 
-> Research-scanning might be detected as abuse, and thus DNS queries are not properly resolved, leading to secondary measure ment errors.

Idea: Write intermediate resolver that:
-> either round-robins queries to distribute the load.
-> or queries M out of N upstream resolvers in parallel and builds a consensus
-> allows to use different operation modes or filters.

