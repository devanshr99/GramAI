/**
 * GramAI - Frontend Application
 * Offline AI Assistant for Rural India
 *
 * Handles chat interaction, voice input/output, UI state,
 * and multi-language support.
 */

(function () {
  'use strict';

  // ============ Configuration ============
  const API_BASE = window.location.origin;
  const ENDPOINTS = {
    query: `${API_BASE}/api/chat/query`,
    search: `${API_BASE}/api/chat/search`,
    languages: `${API_BASE}/api/chat/languages`,
    transcribe: `${API_BASE}/api/voice/transcribe`,
    transcribeBase64: `${API_BASE}/api/voice/transcribe-base64`,
    speak: `${API_BASE}/api/voice/speak`,
    health: `${API_BASE}/api/health`,
    status: `${API_BASE}/api/status`,
    voiceStatus: `${API_BASE}/api/voice/status`,
  };

  // ============ Translations (i18n) ============
  const TRANSLATIONS = {
    hi: {
      loading: 'ग्रामAI लोड हो रहा है...',
      subtitle: 'ऑफ़लाइन AI सहायक',
      selectTopic: 'विषय चुनें',
      catAgri: 'कृषि',
      catHealth: 'स्वास्थ्य',
      catEdu: 'शिक्षा',
      catSchemes: 'सरकारी योजना',
      greeting: 'नमस्ते!',
      welcomeMsg: 'मैं ग्रामAI हूँ। कृषि, स्वास्थ्य, शिक्षा या सरकारी योजनाओं के बारे में पूछें।',
      welcomeHint: 'बोलकर या लिखकर सवाल पूछ सकते हैं।',
      inputPlaceholder: 'यहाँ सवाल लिखें...',
      online: 'चालू',
      offline: 'ऑफ़लाइन',
      speak: 'बोलिए...',
      recognizing: 'आवाज़ पहचानी जा रही है...',
      recognized: 'पहचाना',
      noSpeech: 'आवाज़ नहीं पहचानी जा सकी। दोबारा बोलें।',
      voiceUnavailable: 'वॉइस सेवा उपलब्ध नहीं है। कृपया टाइप करें।',
      voiceConnectError: 'वॉइस सेवा से कनेक्ट नहीं हो पा रहा।',
      micUnavailable: 'माइक्रोफोन उपलब्ध नहीं है',
      error: 'कुछ गड़बड़ हुई। कृपया दोबारा कोशिश करें।',
      allTopics: 'सभी विषय दिखाए जा रहे हैं',
      topicSelected: 'विषय चुना गया',
      llmUnavailable: 'AI मॉडल उपलब्ध नहीं है। ज्ञान आधार से जवाब दिया जाएगा।',
      langChanged: 'भाषा बदली गई',
      ttsUnavailable: 'आवाज़ सेवा उपलब्ध नहीं है',
      source: 'स्रोत',
      installTitle: 'ग्रामAI इंस्टॉल करें',
      installDesc: 'ऐप को अपने फ़ोन में इंस्टॉल करें',
      installBtnText: 'इंस्टॉल',
    },
    en: {
      loading: 'GramAI is loading...',
      subtitle: 'Offline AI Assistant',
      selectTopic: 'Select Topic',
      catAgri: 'Agriculture',
      catHealth: 'Health',
      catEdu: 'Education',
      catSchemes: 'Govt. Schemes',
      greeting: 'Hello!',
      welcomeMsg: 'I am GramAI. Ask me about agriculture, health, education, or government schemes.',
      welcomeHint: 'You can ask by speaking or typing.',
      inputPlaceholder: 'Type your question here...',
      online: 'Online',
      offline: 'Offline',
      speak: 'Speak now...',
      recognizing: 'Recognizing speech...',
      recognized: 'Recognized',
      noSpeech: 'Could not recognize speech. Please try again.',
      voiceUnavailable: 'Voice service unavailable. Please type instead.',
      voiceConnectError: 'Cannot connect to voice service.',
      micUnavailable: 'Microphone not available',
      error: 'Something went wrong. Please try again.',
      allTopics: 'Showing all topics',
      topicSelected: 'topic selected',
      llmUnavailable: 'AI model not available. Answering from knowledge base.',
      langChanged: 'Language changed',
      ttsUnavailable: 'Voice output not available',
      source: 'Source',
      installTitle: 'Install GramAI',
      installDesc: 'Add this app to your home screen',
      installBtnText: 'Install',
    },
    ta: {
      loading: 'GramAI ஏற்றப்படுகிறது...',
      subtitle: 'ஆஃப்லைன் AI உதவியாளர்',
      selectTopic: 'தலைப்பை தேர்ந்தெடுக்கவும்',
      catAgri: 'விவசாயம்',
      catHealth: 'சுகாதாரம்',
      catEdu: 'கல்வி',
      catSchemes: 'அரசு திட்டங்கள்',
      greeting: 'வணக்கம்!',
      welcomeMsg: 'நான் GramAI. விவசாயம், சுகாதாரம், கல்வி அல்லது அரசு திட்டங்கள் பற்றி கேளுங்கள்.',
      welcomeHint: 'பேசி அல்லது தட்டச்சு செய்து கேளுங்கள்.',
      inputPlaceholder: 'உங்கள் கேள்வியை இங்கே எழுதுங்கள்...',
      online: 'இணைப்பு', offline: 'ஆஃப்லைன்',
      speak: 'பேசுங்கள்...', recognizing: 'குரல் அடையாளம் காணப்படுகிறது...',
      recognized: 'அடையாளம் காணப்பட்டது', noSpeech: 'குரலை அடையாளம் காண முடியவில்லை.',
      voiceUnavailable: 'குரல் சேவை கிடைக்கவில்லை.', voiceConnectError: 'குரல் சேவையுடன் இணைக்க முடியவில்லை.',
      micUnavailable: 'மைக்ரோஃபோன் கிடைக்கவில்லை', error: 'ஏதோ தவறு நடந்தது.',
      allTopics: 'அனைத்து தலைப்புகளும் காட்டப்படுகின்றன', topicSelected: 'தலைப்பு தேர்ந்தெடுக்கப்பட்டது',
      llmUnavailable: 'AI மாடல் கிடைக்கவில்லை.', langChanged: 'மொழி மாற்றப்பட்டது',
      ttsUnavailable: 'குரல் வெளியீடு கிடைக்கவில்லை', source: 'மூலம்',
    },
    te: {
      loading: 'GramAI లోడ్ అవుతోంది...', subtitle: 'ఆఫ్‌లైన్ AI సహాయకుడు',
      selectTopic: 'అంశాన్ని ఎంచుకోండి', catAgri: 'వ్యవసాయం', catHealth: 'ఆరోగ్యం',
      catEdu: 'విద్య', catSchemes: 'ప్రభుత్వ పథకాలు',
      greeting: 'నమస్కారం!', welcomeMsg: 'నేను GramAI. వ్యవసాయం, ఆరోగ్యం, విద్య లేదా ప్రభుత్వ పథకాల గురించి అడగండి.',
      welcomeHint: 'మాట్లాడి లేదా టైప్ చేసి అడగండి.',
      inputPlaceholder: 'మీ ప్రశ్నను ఇక్కడ రాయండి...',
      online: 'ఆన్‌లైన్', offline: 'ఆఫ్‌లైన్', speak: 'మాట్లాడండి...', recognizing: 'గుర్తిస్తోంది...',
      recognized: 'గుర్తించబడింది', noSpeech: 'గుర్తించలేకపోయింది.', voiceUnavailable: 'వాయిస్ సేవ అందుబాటులో లేదు.',
      voiceConnectError: 'వాయిస్ సేవకు కనెక్ట్ కాలేదు.', micUnavailable: 'మైక్రోఫోన్ అందుబాటులో లేదు',
      error: 'ఏదో తప్పు జరిగింది.', allTopics: 'అన్ని అంశాలు చూపబడుతున్నాయి', topicSelected: 'అంశం ఎంపిక చేయబడింది',
      llmUnavailable: 'AI మోడల్ అందుబాటులో లేదు.', langChanged: 'భాష మార్చబడింది',
      ttsUnavailable: 'వాయిస్ అవుట్‌పుట్ అందుబాటులో లేదు', source: 'మూలం',
    },
    bn: {
      loading: 'GramAI লোড হচ্ছে...', subtitle: 'অফলাইন AI সহকারী',
      selectTopic: 'বিষয় নির্বাচন করুন', catAgri: 'কৃষি', catHealth: 'স্বাস্থ্য',
      catEdu: 'শিক্ষা', catSchemes: 'সরকারি প্রকল্প',
      greeting: 'নমস্কার!', welcomeMsg: 'আমি GramAI। কৃষি, স্বাস্থ্য, শিক্ষা বা সরকারি প্রকল্প সম্পর্কে জিজ্ঞাসা করুন।',
      welcomeHint: 'বলে বা লিখে প্রশ্ন করতে পারেন।',
      inputPlaceholder: 'আপনার প্রশ্ন এখানে লিখুন...',
      online: 'অনলাইন', offline: 'অফলাইন', speak: 'বলুন...', recognizing: 'শনাক্ত করা হচ্ছে...',
      recognized: 'শনাক্ত হয়েছে', noSpeech: 'শনাক্ত করা যায়নি।', voiceUnavailable: 'ভয়েস সেবা উপলব্ধ নয়।',
      voiceConnectError: 'ভয়েস সেবায় সংযুক্ত হতে পারছে না।', micUnavailable: 'মাইক্রোফোন উপলব্ধ নয়',
      error: 'কিছু সমস্যা হয়েছে।', allTopics: 'সব বিষয় দেখানো হচ্ছে', topicSelected: 'বিষয় নির্বাচিত',
      llmUnavailable: 'AI মডেল উপলব্ধ নয়।', langChanged: 'ভাষা পরিবর্তন হয়েছে',
      ttsUnavailable: 'ভয়েস আউটপুট উপলব্ধ নয়', source: 'উৎস',
    },
    mr: {
      loading: 'GramAI लोड होत आहे...', subtitle: 'ऑफलाइन AI सहाय्यक',
      selectTopic: 'विषय निवडा', catAgri: 'शेती', catHealth: 'आरोग्य',
      catEdu: 'शिक्षण', catSchemes: 'सरकारी योजना',
      greeting: 'नमस्कार!', welcomeMsg: 'मी GramAI आहे. शेती, आरोग्य, शिक्षण किंवा सरकारी योजनांबद्दल विचारा.',
      welcomeHint: 'बोलून किंवा टाइप करून प्रश्न विचारा.',
      inputPlaceholder: 'तुमचा प्रश्न इथे लिहा...',
      online: 'ऑनलाइन', offline: 'ऑफलाइन', speak: 'बोला...', recognizing: 'ओळखत आहे...',
      recognized: 'ओळखले', noSpeech: 'ओळखता आले नाही.', voiceUnavailable: 'व्हॉइस सेवा उपलब्ध नाही.',
      voiceConnectError: 'व्हॉइस सेवेशी जोडता येत नाही.', micUnavailable: 'माइक्रोफोन उपलब्ध नाही',
      error: 'काहीतरी चूक झाली.', allTopics: 'सर्व विषय दाखवले जात आहेत', topicSelected: 'विषय निवडला',
      llmUnavailable: 'AI मॉडेल उपलब्ध नाही.', langChanged: 'भाषा बदलली',
      ttsUnavailable: 'आवाज सेवा उपलब्ध नाही', source: 'स्रोत',
    },
    gu: {
      loading: 'GramAI લોડ થઈ રહ્યું છે...', subtitle: 'ઑફલાઇન AI સહાયક',
      selectTopic: 'વિષય પસંદ કરો', catAgri: 'ખેતી', catHealth: 'આરોગ્ય',
      catEdu: 'શિક્ષણ', catSchemes: 'સરકારી યોજના',
      greeting: 'નમસ્તે!', welcomeMsg: 'હું GramAI છું. ખેતી, આરોગ્ય, શિક્ષણ કે સરકારી યોજનાઓ વિશે પૂછો.',
      welcomeHint: 'બોલીને કે ટાઇપ કરીને પ્રશ્ન પૂછી શકો છો.',
      inputPlaceholder: 'તમારો પ્રશ્ન અહીં લખો...',
      online: 'ઑનલાઇન', offline: 'ઑફલાઇન', speak: 'બોલો...', recognizing: 'ઓળખી રહ્યા છે...',
      recognized: 'ઓળખાયું', noSpeech: 'ઓળખી શકાયું નહીં.', voiceUnavailable: 'વૉઇસ સેવા ઉપલબ્ધ નથી.',
      voiceConnectError: 'વૉઇસ સેવા સાથે જોડાઈ શકાતું નથી.', micUnavailable: 'માઇક્રોફોન ઉપલબ્ધ નથી',
      error: 'કંઈક ખોટું થયું.', allTopics: 'બધા વિષયો બતાવવામાં આવી રહ્યા છે', topicSelected: 'વિષય પસંદ થયો',
      llmUnavailable: 'AI મોડેલ ઉપલબ્ધ નથી.', langChanged: 'ભાષા બદલાઈ',
      ttsUnavailable: 'અવાજ સેવા ઉપલબ્ધ નથી', source: 'સ્રોત',
    },
    kn: {
      loading: 'GramAI ಲೋಡ್ ಆಗುತ್ತಿದೆ...', subtitle: 'ಆಫ್‌ಲೈನ್ AI ಸಹಾಯಕ',
      selectTopic: 'ವಿಷಯ ಆಯ್ಕೆ ಮಾಡಿ', catAgri: 'ಕೃಷಿ', catHealth: 'ಆರೋಗ್ಯ',
      catEdu: 'ಶಿಕ್ಷಣ', catSchemes: 'ಸರ್ಕಾರಿ ಯೋಜನೆ',
      greeting: 'ನಮಸ್ಕಾರ!', welcomeMsg: 'ನಾನು GramAI. ಕೃಷಿ, ಆರೋಗ್ಯ, ಶಿಕ್ಷಣ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ.',
      welcomeHint: 'ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ ಕೇಳಿ.',
      inputPlaceholder: 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಬರೆಯಿರಿ...',
      online: 'ಆನ್‌ಲೈನ್', offline: 'ಆಫ್‌ಲೈನ್', speak: 'ಮಾತನಾಡಿ...', recognizing: 'ಗುರುತಿಸುತ್ತಿದೆ...',
      recognized: 'ಗುರುತಿಸಲಾಯಿತು', noSpeech: 'ಗುರುತಿಸಲಾಗಲಿಲ್ಲ.',
      voiceUnavailable: 'ಧ್ವನಿ ಸೇವೆ ಲಭ್ಯವಿಲ್ಲ.', voiceConnectError: 'ಧ್ವನಿ ಸೇವೆಗೆ ಸಂಪರ್ಕಿಸಲಾಗಲಿಲ್ಲ.',
      micUnavailable: 'ಮೈಕ್ರೋಫೋನ್ ಲಭ್ಯವಿಲ್ಲ', error: 'ಏನೋ ತಪ್ಪಾಯಿತು.',
      allTopics: 'ಎಲ್ಲಾ ವಿಷಯಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ', topicSelected: 'ವಿಷಯ ಆಯ್ಕೆಯಾಯಿತು',
      llmUnavailable: 'AI ಮಾಡೆಲ್ ಲಭ್ಯವಿಲ್ಲ.', langChanged: 'ಭಾಷೆ ಬದಲಾಯಿತು',
      ttsUnavailable: 'ಧ್ವನಿ ಔಟ್‌ಪುಟ್ ಲಭ್ಯವಿಲ್ಲ', source: 'ಮೂಲ',
    },
    ml: {
      loading: 'GramAI ലോഡ് ചെയ്യുന്നു...', subtitle: 'ഓഫ്‌ലൈൻ AI സഹായി',
      selectTopic: 'വിഷയം തിരഞ്ഞെടുക്കുക', catAgri: 'കൃഷി', catHealth: 'ആരോഗ്യം',
      catEdu: 'വിദ്യാഭ്യാസം', catSchemes: 'സർക്കാർ പദ്ധതികൾ',
      greeting: 'നമസ്കാരം!', welcomeMsg: 'ഞാൻ GramAI ആണ്. കൃഷി, ആരോഗ്യം, വിദ്യാഭ്യാസം, സർക്കാർ പദ്ധതികൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കൂ.',
      welcomeHint: 'സംസാരിച്ചോ ടൈപ്പ് ചെയ്‌തോ ചോദിക്കാം.',
      inputPlaceholder: 'നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...',
      online: 'ഓൺലൈൻ', offline: 'ഓഫ്‌ലൈൻ', speak: 'സംസാരിക്കുക...', recognizing: 'തിരിച്ചറിയുന്നു...',
      recognized: 'തിരിച്ചറിഞ്ഞു', noSpeech: 'തിരിച്ചറിയാനായില്ല.',
      voiceUnavailable: 'വോയ്‌സ് സേവനം ലഭ്യമല്ല.', voiceConnectError: 'വോയ്‌സ് സേവനത്തിലേക്ക് കണക്ട് ചെയ്യാനായില്ല.',
      micUnavailable: 'മൈക്രോഫോൺ ലഭ്യമല്ല', error: 'എന്തോ തെറ്റ് സംഭവിച്ചു.',
      allTopics: 'എല്ലാ വിഷയങ്ങളും കാണിക്കുന്നു', topicSelected: 'വിഷയം തിരഞ്ഞെടുത്തു',
      llmUnavailable: 'AI മോഡൽ ലഭ്യമല്ല.', langChanged: 'ഭാഷ മാറ്റി',
      ttsUnavailable: 'ശബ്ദ ഔട്ട്‌പുട്ട് ലഭ്യമല്ല', source: 'ഉറവിടം',
    },
    pa: {
      loading: 'GramAI ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...', subtitle: 'ਆਫ਼ਲਾਈਨ AI ਸਹਾਇਕ',
      selectTopic: 'ਵਿਸ਼ਾ ਚੁਣੋ', catAgri: 'ਖੇਤੀ', catHealth: 'ਸਿਹਤ',
      catEdu: 'ਸਿੱਖਿਆ', catSchemes: 'ਸਰਕਾਰੀ ਯੋਜਨਾ',
      greeting: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ!', welcomeMsg: 'ਮੈਂ GramAI ਹਾਂ। ਖੇਤੀ, ਸਿਹਤ, ਸਿੱਖਿਆ ਜਾਂ ਸਰਕਾਰੀ ਯੋਜਨਾਵਾਂ ਬਾਰੇ ਪੁੱਛੋ।',
      welcomeHint: 'ਬੋਲ ਕੇ ਜਾਂ ਲਿਖ ਕੇ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ।',
      inputPlaceholder: 'ਆਪਣਾ ਸਵਾਲ ਇੱਥੇ ਲਿਖੋ...',
      online: 'ਔਨਲਾਈਨ', offline: 'ਆਫ਼ਲਾਈਨ', speak: 'ਬੋਲੋ...', recognizing: 'ਪਛਾਣ ਰਿਹਾ ਹੈ...',
      recognized: 'ਪਛਾਣਿਆ', noSpeech: 'ਪਛਾਣ ਨਹੀਂ ਹੋ ਸਕੀ।',
      voiceUnavailable: 'ਵੌਇਸ ਸੇਵਾ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।', voiceConnectError: 'ਵੌਇਸ ਸੇਵਾ ਨਾਲ ਜੁੜ ਨਹੀਂ ਸਕਿਆ।',
      micUnavailable: 'ਮਾਈਕ੍ਰੋਫ਼ੋਨ ਉਪਲਬਧ ਨਹੀਂ', error: 'ਕੁਝ ਗਲਤ ਹੋ ਗਿਆ।',
      allTopics: 'ਸਾਰੇ ਵਿਸ਼ੇ ਦਿਖਾਏ ਜਾ ਰਹੇ ਹਨ', topicSelected: 'ਵਿਸ਼ਾ ਚੁਣਿਆ ਗਿਆ',
      llmUnavailable: 'AI ਮਾਡਲ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।', langChanged: 'ਭਾਸ਼ਾ ਬਦਲੀ ਗਈ',
      ttsUnavailable: 'ਆਵਾਜ਼ ਸੇਵਾ ਉਪਲਬਧ ਨਹੀਂ', source: 'ਸਰੋਤ',
    },
  };

  // TTS language codes
  const TTS_CODES = {
    hi: 'hi-IN', en: 'en-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN',
    mr: 'mr-IN', gu: 'gu-IN', kn: 'kn-IN', ml: 'ml-IN', pa: 'pa-IN',
  };

  // ============ State ============
  const state = {
    selectedCategory: null,
    isRecording: false,
    isProcessing: false,
    mediaRecorder: null,
    audioChunks: [],
    chatHistory: [],
    useLLM: true,
    language: localStorage.getItem('gramai_lang') || 'hi',
  };

  // ============ DOM Elements ============
  const $ = (id) => document.getElementById(id);
  const dom = {
    loadingOverlay: $('loadingOverlay'),
    chatArea: $('chatArea'),
    chatWelcome: $('chatWelcome'),
    chatInput: $('chatInput'),
    btnMic: $('btnMic'),
    btnSend: $('btnSend'),
    categoryGrid: $('categoryGrid'),
    quickActions: $('quickActions'),
    statusDot: $('statusDot'),
    statusText: $('statusText'),
    toast: $('toast'),
    installBanner: $('installBanner'),
    installBtn: $('installBtn'),
    installClose: $('installClose'),
    langBtn: $('langBtn'),
    langDropdown: $('langDropdown'),
    langSelector: $('langSelector'),
    langCode: $('langCode'),
  };

  // ============ i18n Helper ============
  function t(key) {
    const strings = TRANSLATIONS[state.language] || TRANSLATIONS['hi'];
    return strings[key] || TRANSLATIONS['hi'][key] || key;
  }

  function applyTranslations() {
    // Update all data-i18n elements
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      el.textContent = t(key);
    });
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = t(key);
    });
    // Update HTML lang attribute
    document.documentElement.lang = state.language === 'en' ? 'en' : state.language;
  }

  // ============ Initialization ============
  async function init() {
    setupEventListeners();
    setActiveLanguage(state.language);
    applyTranslations();
    await checkServerHealth();
    hideLoading();
    autoResizeInput();
  }

  function hideLoading() {
    setTimeout(() => {
      dom.loadingOverlay.classList.add('hidden');
    }, 800);
  }

  // ============ Event Listeners ============
  function setupEventListeners() {
    // Send button
    dom.btnSend.addEventListener('click', handleSend);

    // Enter to send (Shift+Enter for newline)
    dom.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    // Enable/disable send button
    dom.chatInput.addEventListener('input', () => {
      dom.btnSend.disabled = !dom.chatInput.value.trim();
      autoResizeInput();
    });

    // Microphone button
    dom.btnMic.addEventListener('click', handleMicClick);

    // Category cards
    document.querySelectorAll('.category-card').forEach((card) => {
      card.addEventListener('click', () => {
        selectCategory(card.dataset.category);
      });
    });

    // Quick action buttons
    document.querySelectorAll('.quick-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const query = btn.dataset.query;
        dom.chatInput.value = query;
        dom.btnSend.disabled = false;
        handleSend();
      });
    });

    // Language selector
    dom.langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dom.langSelector.classList.toggle('open');
    });

    // Language options
    document.querySelectorAll('.lang-option').forEach((opt) => {
      opt.addEventListener('click', () => {
        const lang = opt.dataset.lang;
        changeLanguage(lang);
      });
    });

    // Close dropdown on outside click
    document.addEventListener('click', () => {
      dom.langSelector.classList.remove('open');
    });

    dom.langDropdown.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // ============ Language Switching ============
  function changeLanguage(lang) {
    state.language = lang;
    localStorage.setItem('gramai_lang', lang);
    setActiveLanguage(lang);
    applyTranslations();
    dom.langSelector.classList.remove('open');
    showToast(`${t('langChanged')}: ${dom.langCode.textContent}`);
  }

  function setActiveLanguage(lang) {
    // Update button label
    const langNames = {
      hi: 'हिंदी', en: 'English', ta: 'தமிழ்', te: 'తెలుగు', bn: 'বাংলা',
      mr: 'मराठी', gu: 'ગુજરાતી', kn: 'ಕನ್ನಡ', ml: 'മലയാളം', pa: 'ਪੰਜਾਬੀ',
    };
    dom.langCode.textContent = langNames[lang] || lang;

    // Update active state in dropdown
    document.querySelectorAll('.lang-option').forEach((opt) => {
      opt.classList.toggle('active', opt.dataset.lang === lang);
    });
  }

  // ============ Auto-resize Input ============
  function autoResizeInput() {
    dom.chatInput.style.height = 'auto';
    dom.chatInput.style.height = Math.min(dom.chatInput.scrollHeight, 120) + 'px';
  }

  // ============ Category Selection ============
  function selectCategory(category) {
    // Toggle
    if (state.selectedCategory === category) {
      state.selectedCategory = null;
      document.querySelectorAll('.category-card').forEach((c) => c.classList.remove('active'));
      showToast(t('allTopics'));
      return;
    }

    state.selectedCategory = category;
    document.querySelectorAll('.category-card').forEach((c) => c.classList.remove('active'));
    document.querySelector(`[data-category="${category}"]`).classList.add('active');

    const categoryIcons = { 'कृषि': '🌱', 'स्वास्थ्य': '🏥', 'शिक्षा': '📚', 'सरकारी योजना': '🏛️' };
    showToast(`${categoryIcons[category] || ''} ${t('topicSelected')}`);
  }

  // ============ Send Message ============
  async function handleSend() {
    const text = dom.chatInput.value.trim();
    if (!text || state.isProcessing) return;

    // Clear input
    dom.chatInput.value = '';
    dom.btnSend.disabled = true;
    autoResizeInput();

    // Hide welcome
    if (dom.chatWelcome) {
      dom.chatWelcome.style.display = 'none';
    }

    // Add user message
    addMessage('user', text);

    // Show typing indicator
    const typingEl = addTypingIndicator();

    // Process query
    state.isProcessing = true;
    try {
      const result = await sendQuery(text);
      removeTypingIndicator(typingEl);
      addMessage('bot', result.response, result.sources);
    } catch (error) {
      removeTypingIndicator(typingEl);
      addMessage('bot', `⚠️ ${t('error')}\nError: ${error.message}`);
    }
    state.isProcessing = false;
  }

  // ============ API Calls ============
  async function sendQuery(query) {
    const response = await fetch(ENDPOINTS.query, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        category: state.selectedCategory,
        use_llm: state.useLLM,
        language: state.language,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    return await response.json();
  }

  async function checkServerHealth() {
    try {
      const response = await fetch(ENDPOINTS.health);
      if (response.ok) {
        dom.statusDot.classList.remove('offline');
        dom.statusText.textContent = t('online');

        // Check detailed status
        try {
          const statusRes = await fetch(ENDPOINTS.status);
          if (statusRes.ok) {
            const status = await statusRes.json();
            const llmOk = status.services?.llm?.available;
            if (!llmOk) {
              state.useLLM = false;
              showToast(`⚠️ ${t('llmUnavailable')}`);
            }
          }
        } catch (e) {
          // Status check failed, use defaults
        }
      } else {
        setOfflineStatus();
      }
    } catch {
      setOfflineStatus();
    }
  }

  function setOfflineStatus() {
    dom.statusDot.classList.add('offline');
    dom.statusText.textContent = t('offline');
    state.useLLM = false;
  }

  // ============ Chat UI ============
  function addMessage(role, text, sources = []) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role} fade-in`;

    const avatar = role === 'bot' ? '🌾' : '👤';
    const time = new Date().toLocaleTimeString(TTS_CODES[state.language] || 'hi-IN', { hour: '2-digit', minute: '2-digit' });

    let sourcesHTML = '';
    if (sources && sources.length > 0) {
      const tags = sources
        .filter(s => s.title)
        .map((s) => `<span class="source-tag">${s.category}: ${s.title}</span>`)
        .join('');
      if (tags) {
        sourcesHTML = `<div class="message-sources">📖 ${t('source')}: ${tags}</div>`;
      }
    }

    // Format text (support basic markdown-like formatting)
    const formattedText = formatText(text);

    messageEl.innerHTML = `
      <div class="message-avatar">${avatar}</div>
      <div class="message-bubble">
        <div class="message-text">${formattedText}</div>
        ${sourcesHTML}
        <div class="message-time">${time}</div>
        ${role === 'bot' ? `
          <div class="audio-player">
            <button onclick="gramAI.speakText(this, \`${escapeBacktick(text)}\`)" title="🔊">🔊</button>
          </div>
        ` : ''}
      </div>
    `;

    dom.chatArea.appendChild(messageEl);
    scrollToBottom();

    // Save to history
    state.chatHistory.push({ role, text, time });
  }

  function formatText(text) {
    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Newlines
    text = text.replace(/\n/g, '<br>');
    return text;
  }

  function escapeBacktick(text) {
    return text.replace(/`/g, '\\`').replace(/\$/g, '\\$');
  }

  function addTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'message bot fade-in';
    el.id = 'typingIndicator';
    el.innerHTML = `
      <div class="message-avatar">🌾</div>
      <div class="message-bubble">
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    dom.chatArea.appendChild(el);
    scrollToBottom();
    return el;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) {
      el.parentNode.removeChild(el);
    }
  }

  function scrollToBottom() {
    dom.chatArea.scrollTop = dom.chatArea.scrollHeight;
  }

  // ============ Voice Input ============
  async function handleMicClick() {
    if (state.isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
        }
      });

      state.audioChunks = [];
      state.mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg',
      });

      state.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          state.audioChunks.push(e.data);
        }
      };

      state.mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        await processRecordedAudio();
      };

      state.mediaRecorder.start();
      state.isRecording = true;
      dom.btnMic.classList.add('recording');
      dom.btnMic.innerHTML = '⏹️';
      showToast(`🎤 ${t('speak')}`);

    } catch (error) {
      console.error('Microphone error:', error);
      showToast(`⚠️ ${t('micUnavailable')}`);
    }
  }

  function stopRecording() {
    if (state.mediaRecorder && state.isRecording) {
      state.mediaRecorder.stop();
      state.isRecording = false;
      dom.btnMic.classList.remove('recording');
      dom.btnMic.innerHTML = '🎤';
    }
  }

  async function processRecordedAudio() {
    if (state.audioChunks.length === 0) return;

    showToast(`🔄 ${t('recognizing')}`);

    const audioBlob = new Blob(state.audioChunks, { type: 'audio/webm' });

    try {
      // Send as file upload
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');

      const response = await fetch(ENDPOINTS.transcribe, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success && result.text) {
          dom.chatInput.value = result.text;
          dom.btnSend.disabled = false;
          showToast(`✅ ${t('recognized')}: "${result.text}"`);
          // Auto-send
          handleSend();
        } else {
          showToast(`⚠️ ${t('noSpeech')}`);
        }
      } else {
        showToast(`⚠️ ${t('voiceUnavailable')}`);
      }
    } catch (error) {
      console.error('STT error:', error);
      showToast(`⚠️ ${t('voiceConnectError')}`);
    }
  }

  // ============ Text-to-Speech ============
  async function speakText(buttonEl, text) {
    // Clean text for speech
    const cleanText = text
      .replace(/<[^>]*>/g, '')
      .replace(/\*\*/g, '')
      .replace(/⚠️|✅|📖|🌾|🏥|📚|🏛️|💰|🤒|🎓|🌿|🌱/g, '')
      .trim();

    if (!cleanText) return;

    // Try server TTS first
    try {
      buttonEl.innerHTML = '⏳';

      const response = await fetch(ENDPOINTS.speak, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        audio.onended = () => {
          buttonEl.innerHTML = '🔊';
          URL.revokeObjectURL(audioUrl);
        };
        return;
      }
    } catch (e) {
      console.warn('Server TTS failed, trying browser TTS');
    }

    // Fallback: Browser SpeechSynthesis API (uses current language)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = TTS_CODES[state.language] || 'hi-IN';
      utterance.rate = 0.9;
      utterance.onend = () => { buttonEl.innerHTML = '🔊'; };
      speechSynthesis.speak(utterance);
    } else {
      showToast(`⚠️ ${t('ttsUnavailable')}`);
      buttonEl.innerHTML = '🔊';
    }
  }

  // ============ Toast ============
  function showToast(message, duration = 3000) {
    dom.toast.textContent = message;
    dom.toast.classList.add('show');
    setTimeout(() => {
      dom.toast.classList.remove('show');
    }, duration);
  }

  // ============ PWA Install Prompt ============
  let deferredPrompt = null;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Show install banner after a short delay
    setTimeout(() => {
      if (dom.installBanner && !localStorage.getItem('gramai_install_dismissed')) {
        dom.installBanner.classList.add('show');
      }
    }, 3000);
  });

  function setupInstallListeners() {
    if (dom.installBtn) {
      dom.installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
          showToast('✅ App installed!');
        }
        deferredPrompt = null;
        dom.installBanner.classList.remove('show');
      });
    }
    if (dom.installClose) {
      dom.installClose.addEventListener('click', () => {
        dom.installBanner.classList.remove('show');
        localStorage.setItem('gramai_install_dismissed', '1');
      });
    }
  }

  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    if (dom.installBanner) dom.installBanner.classList.remove('show');
    console.log('[PWA] App installed successfully');
  });

  // ============ Expose globals ============
  window.gramAI = {
    speakText,
  };

  // ============ Start ============
  document.addEventListener('DOMContentLoaded', () => {
    init();
    setupInstallListeners();
  });

})();
