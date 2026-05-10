#!/usr/bin/env bash
set -euo pipefail

compiler="${CURSED_COMPILER:-/home/ec2-user/cursed/zig-out/bin/cursed-compiler}"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

write_probe() {
  local name="$1"
  local body="$2"
  printf '%s\n' "$body" >"$tmpdir/$name.💀"
}

compile_probe() {
  local name="$1"
  local out="$tmpdir/$name.bin"

  set +e
  "$compiler" --compile --output="$out" "$tmpdir/$name.💀" >"$tmpdir/$name.compile.out" 2>"$tmpdir/$name.compile.err"
  local status=$?
  set -e

  printf 'compile:%s:%s\n' "$name" "$status"
  sed 's/^/compile-stdout:/' "$tmpdir/$name.compile.out"
  sed 's/^/compile-stderr:/' "$tmpdir/$name.compile.err"

  if [[ $status -eq 0 ]]; then
    set +e
    "$out" one two three >"$tmpdir/$name.run.out" 2>"$tmpdir/$name.run.err"
    local run_status=$?
    set -e
    printf 'run:%s:%s\n' "$name" "$run_status"
    printf 'stdout-bytes:%s:' "$name"
    xxd -p "$tmpdir/$name.run.out" | tr -d '\n'
    printf '\n'
    printf 'stderr-bytes:%s:' "$name"
    xxd -p "$tmpdir/$name.run.err" | tr -d '\n'
    printf '\n'
  fi
}

emit_ir_probe() {
  local name="$1"

  set +e
  "$compiler" --emit-ir --output="$tmpdir/$name.ll" "$tmpdir/$name.💀" >"$tmpdir/$name.ir.out" 2>"$tmpdir/$name.ir.err"
  local status=$?
  set -e

  printf 'emit-ir:%s:%s\n' "$name" "$status"
  sed 's/^/ir-stdout:/' "$tmpdir/$name.ir.out"
  sed 's/^/ir-stderr:/' "$tmpdir/$name.ir.err"
  local ir_file
  ir_file="$(find "$tmpdir" -maxdepth 1 -type f -name "$name.ll*" | sort | tail -n 1)"
  if [[ -n "$ir_file" && -f "$ir_file" ]]; then
    grep -n 'newline_str\|cursed_runtime_spill' "$ir_file" | sed 's/^/ir-grep:/'
  fi
}

write_probe baseline 'vibe main
yeet "vibez"

slay main_character() {
    vibez.spill("baseline-stdout")
}'

write_probe spill_two 'vibe main
yeet "vibez"

slay main_character() {
    vibez.spill("A")
    vibez.spill("B")
}'

write_probe argv_runtime 'vibe main
yeet "vibez"

slay main_character() {
    vibez.spill("BEFORE")
    vibez.spill(argv)
    vibez.spill("AFTER")
}'

write_probe unsupported_import 'vibe main
yeet "dropz"

slay main_character() {
    dropz.read_file("x")
}'

write_probe bare_read_file 'vibe main
yeet "vibez"

slay main_character() {
    read_file("x")
}'

write_probe user_defined_function 'vibe main
yeet "vibez"

slay helper() {
    vibez.spill("helper")
}

slay main_character() {
    helper()
}'

write_probe member_access 'vibe main
yeet "vibez"

slay main_character() {
    sus msg tea = "hello"
    vibez.spill(msg.length)
}'

write_probe array_access 'vibe main
yeet "vibez"

slay main_character() {
    sus nums [3]normie = [1, 2, 3]
    vibez.spill(nums[1])
}'

write_probe conditionals 'vibe main
yeet "vibez"

slay main_character() {
    ready 1 {
        vibez.spill("yes")
    }
}'

write_probe loops 'vibe main
yeet "vibez"

slay main_character() {
    bestie 1 {
        vibez.spill("loop")
    }
}'

write_probe binary_expression 'vibe main
yeet "vibez"

slay main_character() {
    sus a normie = 1
    sus b normie = 2
    sus c normie = a + b
    vibez.spill(c)
}'

write_probe assignment 'vibe main
yeet "vibez"

slay main_character() {
    sus x normie = 1
    x = 2
    vibez.spill(x)
}'

for name in \
  baseline \
  spill_two \
  argv_runtime \
  unsupported_import \
  bare_read_file \
  user_defined_function \
  member_access \
  array_access \
  conditionals \
  loops \
  binary_expression \
  assignment
do
  compile_probe "$name"
done

emit_ir_probe spill_two
