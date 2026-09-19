export default function NepaliHome() {
  return <main className="container page"><p className="eyebrow">नेपाली</p><h1>प्रविधि, टुल्स र AI</h1>
    <p className="muted">नेपाली सामग्रीका लागि आधार तयार छ। यहाँ समाचार, गाइड, टुल्स र AI सामग्री थप्न सकिन्छ।</p>
    <div className="listing"><a className="card" href="/tools/"><span className="tag">TOOLS</span><h3>निःशुल्क टुल्स</h3><p>दैनिक कामका लागि उपयोगी वेब टुल्स।</p></a><a className="card" href="/ai/"><span className="tag">AI</span><h3>AI</h3><p>व्यावहारिक AI स्रोत र workflows।</p></a><a className="card" href="/news/"><span className="tag">NEWS</span><h3>प्रविधि समाचार</h3><p>उपयोगी प्रविधि अपडेटहरू।</p></a></div>
  </main>;
}