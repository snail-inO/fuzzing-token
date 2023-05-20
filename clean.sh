#!/bin/bash

rm -rf sc_source/abi/*
rm -rf sc_source/json/*
rm -rf sc_source/sol/*

rm -rf tests/token/result/*
rm -rf tests/token/tmp/*
rm -rf tests/token/*_test.sol

touch tests/token/tmp/args.json