const form = document.querySelector('#assessment-form');
const input = document.querySelector('#password');
const toggle = document.querySelector('#toggle-password');
const clearButton = document.querySelector('#clear-button');
const submitButton = document.querySelector('#submit-button');
const error = document.querySelector('#form-error');
const emptyState = document.querySelector('#empty-state');
const results = document.querySelector('#results');

toggle.addEventListener('click', () => {
  const hidden = input.type === 'password';
  input.type = hidden ? 'text' : 'password';
  toggle.textContent = hidden ? 'Hide' : 'Show';
});

clearButton.addEventListener('click', clearAssessment);

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  error.textContent = '';
  submitButton.disabled = true;
  submitButton.textContent = 'Assessing...';

  try {
    const response = await fetch('/api/assess', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({password: input.value}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Assessment failed.');
    renderResults(data);
    input.value = '';
    input.type = 'password';
toggle.textContent = 'Show';
  } catch (problem) {
    error.textContent = problem.message;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Assess password';
  }
});

function clearAssessment() {
  input.value = '';
  input.type = 'password';
  toggle.textContent = 'Show';
  error.textContent = '';
  results.hidden = true;
  emptyState.hidden = false;
  input.focus();
}

function renderResults(data) {
  const assessment = data.assessment;
  const bandKey = assessment.band.toLowerCase().replaceAll(' ', '-');

const score = document.querySelector('#score');
score.textContent = assessment.score;
score.className = `score score-${bandKey}`;

const scoreColors = {
  Weak: '#b52a2a',
  Fair: '#a66500',
  Strong: '#1976a8',
  'Very Strong': '#208653'
};

score.style.color = scoreColors[assessment.band] || '#142333';

const band = document.querySelector('#band');
band.textContent = assessment.band;
band.className = `band band-${bandKey}`;

  const lengthMet = assessment.standard_checks.single_factor_length_met;
  const common = assessment.standard_checks.common_password_blocked;
  document.querySelector('#standard-result').textContent =
    `${lengthMet ? 'Meets' : 'Does not meet'} the 15-character single-factor length threshold. ` +
    `${common ? 'Found' : 'Not found'} in the local common-password blocklist.`;

  const breach = data.breach;
  const breachResult = document.querySelector('#breach-result');
  breachResult.textContent =
    `${breach.status}${breach.count ? ` (${breach.count.toLocaleString()} recorded appearances)` : ''}. ${breach.message}`;
  const breachCard = breachResult.closest('article');
  breachCard.classList.remove('breach-found', 'breach-not-found', 'breach-unavailable');
  const breachClasses = {
    'Found': 'breach-found',
    'Not Found': 'breach-not-found',
    'Check Unavailable': 'breach-unavailable',
  };
  breachCard.classList.add(breachClasses[breach.status] || 'breach-unavailable');

  const breakdown = document.querySelector('#breakdown');
  breakdown.replaceChildren();
  const labels = {
    length: 'Length',
    character_variety: 'Character variety (informational)',
    predictable_pattern_resistance: 'Predictable-pattern resistance',
    common_password_resistance: 'Common-password resistance',
  };
  Object.entries(assessment.score_breakdown).forEach(([key, value]) => {
    const row = document.createElement('div');
    row.className = 'breakdown-row';
    row.innerHTML = `<span>${labels[key]}</span><strong>${value.points}/${value.maximum}</strong>`;
    breakdown.appendChild(row);
  });

  const list = document.querySelector('#recommendations');
  list.replaceChildren();
  data.recommendations.forEach((recommendation) => {
    const item = document.createElement('li');
    item.textContent = recommendation;
    list.appendChild(item);
  });

  document.querySelector('#result-notice').textContent = data.notice;
  emptyState.hidden = true;
  results.hidden = false;
}
