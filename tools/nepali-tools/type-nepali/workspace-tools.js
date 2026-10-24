(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const editor = $('#editor'), select = $('#document-select'), nameInput = $('#document-name'), status = $('#document-status');
  if (!editor || !select || !nameInput || !status) return;
  const STORAGE_KEY = 'ln-nepali-typing-documents-v1';
  const DRAFT_KEY = 'ln-nepali-typing-draft';
  const MAX_DOCUMENTS = 30;
  let documents = [], currentId = null, idCounter = 0;
  const templates = {
    application: 'मिति: [मिति]\n\nश्रीमान्/श्रीमती [पद/कार्यालय प्रमुख]ज्यू,\n[कार्यालय/संस्थाको नाम]\n\nविषय: [विषय] सम्बन्धमा।\n\nमहोदय/महोदया,\n\n[आफ्नो अनुरोध वा निवेदन यहाँ स्पष्ट रूपमा लेख्नुहोस्।]\n\nधन्यवाद।\n\nनिवेदक: [नाम]\nसम्पर्क: [सम्पर्क विवरण]',
    leave: 'मिति: [मिति]\n\nश्रीमान्/श्रीमती [प्रमुखज्यू],\n[कार्यालय/विद्यालयको नाम]\n\nविषय: बिदा पाऊँ भन्ने सम्बन्धमा।\n\nमहोदय/महोदया,\n\n[कारण] का कारण [सुरु मिति] देखि [अन्तिम मिति] सम्म बिदा आवश्यक भएकाले स्वीकृत गरिदिनुहुन अनुरोध गर्दछु।\n\nनिवेदक: [नाम]',
    office: 'पत्र संख्या: [पत्र संख्या]\nचलानी नं.: [चलानी नं.]\nमिति: [मिति]\n\nश्री [प्राप्तकर्ताको नाम/पद],\n[कार्यालय]\n\nविषय: [विषय]\n\nमहोदय/महोदया,\n\n[पत्रको मुख्य व्यहोरा यहाँ लेख्नुहोस्।]\n\nभवदीय,\n[नाम]\n[पद/कार्यालय]',
    school: 'मिति: [मिति]\n\nश्री प्रधानाध्यापकज्यू,\n[विद्यालयको नाम]\n\nविषय: [विषय] सम्बन्धमा।\n\nमहोदय,\n\n[निवेदनको कारण र अनुरोध यहाँ लेख्नुहोस्।]\n\nनिवेदक: [नाम]\nकक्षा: [कक्षा]',
    minutes: 'बैठकको माइन्युट\n\nमिति: [मिति]    समय: [समय]\nस्थान: [स्थान]\nअध्यक्षता: [नाम]\nउपस्थित सदस्यहरू: [नामहरू]\n\nएजेन्डा:\n१. [एजेन्डा १]\n२. [एजेन्डा २]\n\nनिर्णयहरू:\n१. [निर्णय १]\n२. [निर्णय २]\n\nमाइन्युट तयार गर्ने: [नाम]',
    cv: 'जीवनवृत्त / CV\n\nनाम: [पूरा नाम]\nठेगाना: [ठेगाना]\nसम्पर्क: [फोन/इमेल]\n\nउद्देश्य\n[व्यावसायिक उद्देश्य]\n\nशैक्षिक योग्यता\n[योग्यता, संस्था, वर्ष]\n\nअनुभव\n[पद, संस्था, अवधि, मुख्य जिम्मेवारी]\n\nसीपहरू\n[सीपहरूको सूची]\n\nभाषा\n[भाषाहरू]',
    loksewa: 'लोकसेवा अभ्यास\n\nविषय: [विषय]\nसमय: [समय सीमा]\n\nप्रश्न १. [प्रश्न यहाँ लेख्नुहोस्]\nउत्तर: \n\nप्रश्न २. [प्रश्न यहाँ लेख्नुहोस्]\nउत्तर: \n\nआजको समीक्षा:\nसिकेका कुरा: [मुख्य बुँदा]\nअझ अभ्यास गर्नुपर्ने: [बुँदा]'
  };
  function makeId() { idCounter += 1; return String(Date.now()) + '-' + idCounter; }
  function setStatus(message) { status.textContent = message; }
  function currentDocument() { return documents.find(doc => doc.id === currentId) || null; }
  function persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(documents));
      return true;
    } catch (_) {
      setStatus('Local storage is unavailable or full. Export your text before leaving.');
      return false;
    }
  }
  function renderDocuments() {
    select.replaceChildren();
    if (!documents.length) {
      const option = document.createElement('option');
      option.value = ''; option.textContent = 'No saved documents';
      select.append(option); select.disabled = true;
      nameInput.value = '';
      return;
    }
    select.disabled = false;
    documents.forEach(doc => {
      const option = document.createElement('option');
      option.value = doc.id; option.textContent = doc.name;
      option.selected = doc.id === currentId;
      select.append(option);
    });
    const current = currentDocument();
    nameInput.value = current ? current.name : '';
  }
  function saveCurrent() {
    const doc = currentDocument();
    if (!doc) {
      if (!editor.value) return;
      if (documents.length >= MAX_DOCUMENTS) {
        setStatus('Document limit reached. Delete a document or export your text.');
        return;
      }
      const created = { id: makeId(), name: 'Untitled document', content: editor.value, updatedAt: new Date().toISOString() };
      documents.push(created); currentId = created.id; renderDocuments();
    } else {
      doc.content = editor.value;
      doc.updatedAt = new Date().toISOString();
    }
    if (persist()) setStatus('Saved locally · ' + documents.length + ' document' + (documents.length === 1 ? '' : 's'));
  }
  function syncEditor(content) {
    editor.value = content;
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    editor.focus();
  }
  function createDocument() {
    saveCurrent();
    if (documents.length >= MAX_DOCUMENTS) { setStatus('Up to 30 local documents are supported. Delete one before creating another.'); return; }
    const doc = { id: makeId(), name: 'Untitled document', content: '', updatedAt: new Date().toISOString() };
    documents.push(doc); currentId = doc.id; persist(); renderDocuments(); syncEditor('');
    setStatus('New local document created');
  }
  select.addEventListener('change', () => {
    saveCurrent();
    currentId = select.value || null;
    const doc = currentDocument();
    renderDocuments();
    syncEditor(doc ? doc.content : '');
    setStatus(doc ? 'Opened “' + doc.name + '” locally' : 'No saved document selected');
  });
  $('#new-document').addEventListener('click', createDocument);
  $('#save-document').addEventListener('click', () => { saveCurrent(); setStatus('Document saved in this browser'); });
  $('#rename-document').addEventListener('click', () => {
    const doc = currentDocument(), nextName = nameInput.value.trim();
    if (!doc) { setStatus('Create a document before renaming it'); return; }
    if (!nextName) { setStatus('Enter a document name'); return; }
    doc.name = nextName.slice(0, 80); doc.updatedAt = new Date().toISOString();
    persist(); renderDocuments(); setStatus('Document renamed');
  });
  $('#delete-document').addEventListener('click', () => {
    const doc = currentDocument();
    if (!doc) { setStatus('No document to delete'); return; }
    if (!window.confirm('Delete “' + doc.name + '” from this browser? This cannot be undone.')) return;
    documents = documents.filter(item => item.id !== doc.id);
    currentId = documents.length ? documents[0].id : null;
    persist(); renderDocuments(); syncEditor(currentDocument()?.content || '');
    setStatus('Document deleted from this browser');
  });
  editor.addEventListener('input', saveCurrent);
  editor.addEventListener('change', saveCurrent);
  $('#insert-template').addEventListener('click', () => {
    const key = $('#template-select').value, template = templates[key];
    if (!template) return;
    if (editor.value.trim() && !window.confirm('Replace the current text with this template? Save a copy first if needed.')) return;
    syncEditor(template); setStatus('Template inserted · edit the bracketed placeholders');
  });
  $('#replace-all').addEventListener('click', () => {
    const find = $('#find-text').value;
    if (!find) { setStatus('Enter text to find'); return; }
    const source = editor.value, count = source.split(find).length - 1;
    if (!count) { setStatus('No matches found'); return; }
    syncEditor(source.split(find).join($('#replace-text').value));
    setStatus('Replaced ' + count + ' occurrence' + (count === 1 ? '' : 's'));
  });
  $('#print-document').addEventListener('click', () => window.print());
  $('#delete-local-data').addEventListener('click', () => {
    if (!window.confirm('Delete all saved documents, the current draft and learned typing choices from this browser? This cannot be undone.')) return;
    documents = []; currentId = null;
    try { localStorage.removeItem(STORAGE_KEY); localStorage.removeItem(DRAFT_KEY); localStorage.removeItem('ln-nepali-typing-learned-v1'); } catch (_) {}
    renderDocuments(); syncEditor('');
    try { localStorage.removeItem(STORAGE_KEY); localStorage.removeItem(DRAFT_KEY); } catch (_) {}
    window.dispatchEvent(new Event('ln:clear-local-typing-data'));
    setStatus('Saved text and learned typing choices deleted from this browser');
  });

  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (Array.isArray(saved)) documents = saved.filter(doc => doc && typeof doc.id === 'string' && typeof doc.name === 'string' && typeof doc.content === 'string').slice(0, MAX_DOCUMENTS);
  } catch (_) { documents = []; }
  if (!documents.length) {
    const draft = editor.value || (() => { try { return localStorage.getItem(DRAFT_KEY) || ''; } catch (_) { return ''; } })();
    const initial = { id: makeId(), name: draft.trim() ? 'Recovered draft' : 'Untitled document', content: draft, updatedAt: new Date().toISOString() };
    documents = [initial]; currentId = initial.id; persist();
  } else {
    currentId = documents[0].id;
    const draft = (() => { try { return localStorage.getItem(DRAFT_KEY); } catch (_) { return null; } })();
    if (draft !== null && draft !== currentDocument().content) {
      currentId = makeId();
      documents.unshift({ id: currentId, name: 'Recovered draft', content: draft, updatedAt: new Date().toISOString() });
      documents = documents.slice(0, MAX_DOCUMENTS); persist();
    }
  }
  renderDocuments();
  if (currentDocument() && editor.value !== currentDocument().content) syncEditor(currentDocument().content);
  setStatus('Saved locally · ' + documents.length + ' document' + (documents.length === 1 ? '' : 's'));
})();
