const speakButton = document.getElementById('speak');
const recognition = new window.webkitSpeechRecognition();
recognition.interimResults = false;
recognition.continuous = false;

recognition.onresult = function(event) {
  let transcript = Array.from(event.results)
    .map(result => result[0])
    .map(result => result.transcript)
    .join('');

  transcript = transcript.replace(/flood/g, 'Vlad');

  document.getElementById('question').value = transcript; 
  speakButton.click();  
};

speakButton.onclick = function() {
  recognition.start();
};

document.getElementById('chat-form').addEventListener('submit', function(event) {
  event.preventDefault();

  var question = document.getElementById('question').value;

  fetch('/chat2', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({question: question})
  })
  .then(function(response) {
    if (!response.ok) {
      throw new Error('Response not OK');
    }
    return response.json();
  })
  .then(function(data) {
    document.getElementById('bot-response').textContent = data.answer;

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(data.answer);
    synth.speak(utterance);
  })
  .catch(function(error) {
    console.error('Error:', error);
  });
});
