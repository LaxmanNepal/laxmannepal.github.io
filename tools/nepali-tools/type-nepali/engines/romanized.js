(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.NepaliRomanized = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  const VOWELS = { a:'अ', aa:'आ', i:'इ', ii:'ई', ee:'ई', u:'उ', uu:'ऊ', oo:'ऊ', e:'ए', ai:'ऐ', o:'ओ', au:'औ', ri:'ऋ' };
  const MATRA = { a:'', aa:'ा', i:'ि', ii:'ी', ee:'ी', u:'ु', uu:'ू', oo:'ू', e:'े', ai:'ै', o:'ो', au:'ौ', ri:'ृ' };
  const CONS = { k:'क', kh:'ख', g:'ग', gh:'घ', ng:'ङ', ch:'च', chh:'छ', j:'ज', jh:'झ', ny:'ञ', T:'ट', Th:'ठ', D:'ड', Dh:'ढ', N:'ण', t:'त', th:'थ', d:'द', dh:'ध', n:'न', p:'प', ph:'फ', f:'फ', b:'ब', bh:'भ', m:'म', y:'य', r:'र', l:'ल', w:'व', v:'व', sh:'श', Sh:'ष', s:'स', h:'ह', ksh:'क्ष', tr:'त्र', gy:'ज्ञ', gn:'ज्ञ', L:'ळ' };
  const SPECIAL = {
    om:'ॐ', aum:'ॐ', namaste:'नमस्ते', namaskar:'नमस्कार', nepal:'नेपाल', nepaal:'नेपाल',
    nepali:'नेपाली', mero:'मेरो', desh:'देश', dhanyabad:'धन्यवाद', dhanyavaad:'धन्यवाद',
    dhanyawad:'धन्यवाद', tapai:'तपाईं', tapaai:'तपाईं', lai:'लाई', kasto:'कस्तो',
    chha:'छ', cha:'छ', chhu:'छु', chhuu:'छु', ma:'म', ho:'हो', hajur:'हजुर',
    sanchai:'सन्चै', ramro:'राम्रो', sathi:'साथी', mitra:'मित्र', ghar:'घर',
    pani:'पानी', maya:'माया', samjhana:'सम्झना', shubha:'शुभ', bihana:'बिहान',
    beluka:'बेलुका', aaja:'आज', bholi:'भोलि', hijo:'हिजो', kathmandu:'काठमाडौं',
    pokhara:'पोखरा', bolchhu:'बोल्छु', bolchu:'बोल्छु', garne:'गर्ने', garchhu:'गर्छु',
    chhaina:'छैन', xaina:'छैन', kina:'किन', kasari:'कसरी', ke:'के', kaha:'कहाँ',
    ra:'र', ko:'को', ki:'कि', ka:'का', huncha:'हुन्छ', hunuhunchha:'हुनुहुन्छ',
    bhayo:'भयो', unicode:'युनिकोड', thapa:'थापा', sharma:'शर्मा', laxman:'लक्ष्मण',
    sanai:'सानै', ram:'राम', sita:'सीता'
  };
  const TOKENS = ['ksh','chh','ch','kh','gh','ng','jh','ny','Th','Dh','Sh','sh','th','dh','ph','bh','aa','ii','ee','uu','oo','ai','au','ri','tr','gy','gn'];
  function tokenize(input) {
    const parts = [];
    for (let i = 0; i < input.length;) {
      const tail = input.slice(i);
      const exact = TOKENS.find(token => tail.startsWith(token));
      const insensitive = exact || TOKENS.find(token => tail.slice(0, token.length).toLowerCase() === token.toLowerCase());
      const token = insensitive ? input.slice(i, i + insensitive.length) : input[i];
      parts.push(token);
      i += token.length;
    }
    return parts;
  }
  function transliterate(input) {
    if (typeof input !== 'string' || !input) return '';
    const parts = tokenize(input);
    let out = '';
    for (let i = 0; i < parts.length; i++) {
      const raw = parts[i];
      if (!/[a-z]/i.test(raw)) { out += raw; continue; }
      const consonant = CONS[raw] || CONS[raw.toLowerCase()];
      if (consonant) {
        out += consonant;
        const next = parts[i + 1];
        const nextKey = next && next.toLowerCase();
        if (next && Object.prototype.hasOwnProperty.call(MATRA, nextKey)) {
          out += MATRA[nextKey];
          i++;
        } else if (next && (CONS[next] || CONS[next.toLowerCase()])) {
          out += '्';
        }
        continue;
      }
      const vowel = raw.toLowerCase();
      if (VOWELS[vowel]) out += VOWELS[vowel];
      else out += raw;
    }
    return out;
  }
  function convertWord(word) {
    if (typeof word !== 'string') return '';
    const lower = word.toLowerCase();
    return SPECIAL[lower] || transliterate(word);
  }
  return { transliterate, convertWord, specialWords: Object.keys(SPECIAL) };
});
