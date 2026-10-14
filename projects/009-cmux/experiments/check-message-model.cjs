"use strict";
const assert = require("node:assert/strict");
const { createMessageModel, transitionMessage, messagePresentation } = require("../web/app.js");
let passed = 0;
function check(name, run) { run(); passed += 1; console.log("PASS " + name); }

check("idle Claude exposes a hook wake; idle Codex requires a human prompt", () => {
  const claude = transitionMessage(createMessageModel("claude", "idle"), "send");
  const codex = transitionMessage(createMessageModel("codex", "idle"), "send");
  assert.equal(claude.phase, "queued");
  assert.equal(codex.phase, "queued");
  assert.match(messagePresentation(claude).label, /Hook 唤醒/);
  assert.match(messagePresentation(codex).label, /人提交下一次提示/);
  assert.match(messagePresentation(codex).feedback, /不能主动唤醒/);
});
check("human waits hold delivery for both integrations", () => {
  for (const kind of ["claude", "codex"]) {
    let state = transitionMessage(createMessageModel(kind, "human"), "send");
    assert.match(messagePresentation(state).feedback, /交付暂缓/);
    state = transitionMessage(state, "step");
    assert.equal(state.phase, "queued");
    assert.equal(state.recipientState, "idle");
    assert.equal(transitionMessage(state, "step").phase, "delivered");
  }
});
check("busy Codex uses a stop hook and does not imply arbitrary interruption", () => {
  const state = transitionMessage(createMessageModel("codex", "busy"), "send");
  assert.match(messagePresentation(state).label, /即将停止的 Hook/);
  assert.match(messagePresentation(state).feedback, /不是任意时刻/);
});
check("queued opt-out becomes failed and cannot advance", () => {
  let state = transitionMessage(createMessageModel(), "send");
  state = transitionMessage(state, "disable");
  assert.equal(state.phase, "failed");
  assert.equal(messagePresentation(state).canAdvance, false);
  assert.equal(transitionMessage(state, "step").phase, "failed");
});
check("already delivered messages are not undone by opt-out", () => {
  let state = transitionMessage(createMessageModel(), "send");
  state = transitionMessage(state, "step");
  state = transitionMessage(state, "disable");
  assert.equal(state.phase, "delivered");
  assert.equal(transitionMessage(state, "step").phase, "read");
});
check("read is terminal and explicitly does not certify the task", () => {
  let state = transitionMessage(createMessageModel(), "send");
  state = transitionMessage(state, "step");
  state = transitionMessage(state, "step");
  assert.equal(state.phase, "read");
  assert.match(messagePresentation(state).feedback, /不表示.*任务完成/);
  assert.equal(messagePresentation(state).canAdvance, false);
  assert.equal(transitionMessage(state, "step").phase, "read");
});
check("disabled receivers do not create a queued message", () => {
  const state = transitionMessage(transitionMessage(createMessageModel(), "disable"), "send");
  assert.equal(state.phase, "draft");
});
check("sending twice does not overwrite the current message state", () => {
  const state = transitionMessage(createMessageModel("codex", "idle"), "send");
  assert.deepEqual(transitionMessage(state, "send"), state);
});
check("transitions leave the previous snapshot untouched", () => {
  const original = Object.freeze(createMessageModel("claude", "human"));
  const queued = transitionMessage(original, "send");
  assert.equal(original.phase, "draft");
  assert.equal(queued.phase, "queued");
});
console.log(`${passed} teaching-model checks passed. This does not test upstream hooks.`);
