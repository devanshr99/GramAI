export const offlineDatabase = [
  // Schemes
  { keywords: ["pm-kisan", "kisan", "pm kisan", "6000", "सम्मान निधि"], title: "PM-KISAN योजना", content: "प्रधानमंत्री किसान सम्मान निधि (PM-KISAN) से हर किसान को ₹6,000 सालाना मिलते हैं। ₹2,000 की 3 किस्तें सीधे बैंक खाते में आती हैं। 2 हेक्टेयर तक जमीन वाले किसान पात्र हैं।" },
  { keywords: ["ayushman", "pm-jay", "pmjay", "आयुष्मान", "मुफ्त इलाज", "bpl", "health", "hospital"], title: "आयुष्मान भारत (PM-JAY)", content: "₹5 लाख तक का मुफ्त इलाज। गरीबी रेखा से नीचे (BPL) परिवार पात्र हैं। आयुष्मान कार्ड CSC या अस्पताल में बनवाएं।" },
  { keywords: ["pmay", "housing", "आवास", "पक्का घर", "घर", "house"], title: "प्रधानमंत्री आवास योजना (PMAY)", content: "ग्रामीण क्षेत्र में पक्का घर बनाने के लिए ₹1,20,000 की सहायता मिलती है। ग्राम पंचायत में आवेदन करें।" },
  { keywords: ["pmfby", "फसल बीमा", "crop insurance", "बीमा"], title: "प्रधानमंत्री फसल बीमा योजना (PMFBY)", content: "फसल बीमा योजना से प्राकृतिक आपदा में नुकसान की भरपाई मिलती है। बैंक या CSC से आवेदन करें।" },
  { keywords: ["mgnrega", "nrega", "मनरेगा", "रोजगार", "employment", "जॉब कार्ड", "job"], title: "मनरेगा (MGNREGA)", content: "हर ग्रामीण परिवार को साल में 100 दिन का गारंटीड रोजगार मिलता है। जॉब कार्ड ग्राम पंचायत से बनवाएं।" },
  
  // Agriculture
  { keywords: ["गेहूं", "wheat", "रबी"], title: "गेहूं की खेती", content: "गेहूं रबी सीजन की प्रमुख फसल है। बुवाई का सही समय अक्टूबर-नवंबर है। पहली सिंचाई बुवाई के 21 दिन बाद करें।" },
  { keywords: ["धान", "rice", "paddy", "खरीफ"], title: "धान की खेती", content: "धान खरीफ सीजन की मुख्य फसल है। जून-जुलाई में रोपाई करें। नर्सरी मई में तैयार करें।" },
  { keywords: ["उर्वरक", "fertilizer", "यूरिया", "dap", "npk", "खाद", "urea"], title: "उर्वरक का सही उपयोग", content: "मिट्टी परीक्षण करवाकर ही उर्वरक डालें। यूरिया में 46% नाइट्रोजन होता है। जैविक खाद भी डालें।" },
  { keywords: ["सिंचाई", "irrigation", "ड्रिप", "स्प्रिंकलर", "पानी", "water"], title: "सिंचाई के तरीके", content: "ड्रिप सिंचाई से 60% पानी की बचत होती है। अधिक पानी से फसल को नुकसान होता है।" },
  { keywords: ["जैविक", "organic", "वर्मीकम्पोस्ट", "गोबर"], title: "जैविक खेती", content: "जैविक खेती में रासायनिक उर्वरक का उपयोग नहीं होता। गोबर की खाद, वर्मीकम्पोस्ट, और हरी खाद का उपयोग करें।" },
  
  // Health/Science
  { keywords: ["बुखार", "fever", "paracetamol", "तापमान"], title: "बुखार का प्रबंधन", content: "बुखार आने पर पैरासिटामोल लें और ठंडे पानी की पट्टियां रखें। अगर बुखार 3 दिन से ज्यादा रहे तो डॉक्टर को दिखाएं।" },
  { keywords: ["मच्छर", "mosquito", "dengue", "malaria", "डेंगू", "मलेरिया"], title: "मच्छर जनित रोग", content: "मलेरिया और डेंगू मच्छरों के काटने से होते हैं। आस-पास पानी जमा न होने दें और मच्छरदानी का उपयोग करें।" },
  { keywords: ["pregnancy", "गर्भावस्था", "पोषण", "pregnant"], title: "गर्भावस्था", content: "गर्भवती महिलाओं को आयरन और कैल्शियम की गोलियां लेनी चाहिए और नियमित जांच करवानी चाहिए।" },
  { keywords: ["vaccine", "टीकाकरण", "टीका", "बच्चों", "immunization"], title: "टीकाकरण", content: "बच्चों का समय पर टीकाकरण करवाएं। इससे उन्हें कई गंभीर बीमारियों से बचाया जा सकता है।" }
];

export function fallbackSearch(query) {
  const q = query.toLowerCase();
  
  let bestMatch = null;
  let maxMatches = 0;
  
  for (const item of offlineDatabase) {
    let matches = 0;
    for (const kw of item.keywords) {
      if (q.includes(kw.toLowerCase())) {
        matches++;
      }
    }
    if (matches > maxMatches) {
      maxMatches = matches;
      bestMatch = item;
    }
  }

  if (bestMatch) {
    return `(Offline Mode - No Internet)\n📖 ज्ञान आधार से जानकारी:\n\n**${bestMatch.title}**\n${bestMatch.content}`;
  }
  
  return "(Offline Mode - No Internet)\nकृपया इंटरनेट कनेक्ट करें या कोई अन्य प्रश्न पूछें। मैं बिना इंटरनेट के केवल कुछ मुख्य योजनाओं और खेती की जानकारी दे सकता हूँ।";
}
