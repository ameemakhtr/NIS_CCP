import { useEffect, useState } from 'react'

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
const BLUE = '#1F6C9F'
const AMBER = '#D9A441'

const letterCount = (text) => text.toUpperCase().replace(/[^A-Z]/g, '').length
const inPairs = (text) => text.replace(/(..)/g, '$1 ').trim()
const number = (value) => value.toLocaleString('en-US')

async function api(path, body) {
  let response
  try {
    response = await fetch(path, body && {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error('Cannot reach the Python server. Start it with: python server.py')
  }
  const data = await response.json().catch(() => ({ error: 'The server sent an unreadable reply.' }))
  if (!response.ok) throw new Error(data.error)
  return data
}

function Section({ id, index, title, lead, children }) {
  return (
    <section id={id} className="section reveal">
      <header className="section-head">
        <span className="eyebrow">{index}</span>
        <h2>{title}</h2>
        <p>{lead}</p>
      </header>
      {children}
    </section>
  )
}

function KeyField({ label, value, onChange, placeholder }) {
  const letters = letterCount(value)
  return (
    <label className="field">
      <span className="field-label">
        {label}
        <span className={`count ${value && letters < 10 ? 'short' : ''}`}>{letters} / 10 letters</span>
      </span>
      <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} spellCheck="false" autoComplete="off" />
    </label>
  )
}

function Matrix({ title, rows }) {
  return (
    <div className="matrix-block">
      <span className="tile-label">{title}</span>
      <div className="matrix">
        {rows.flat().map((value, i) => <span key={i}>{value}</span>)}
      </div>
    </div>
  )
}

function Tile({ label, value, note }) {
  return (
    <div className="card tile">
      <span className="tile-label">{label}</span>
      <strong>{value}</strong>
      <span className="tile-note">{note}</span>
    </div>
  )
}

function ErrorNote({ message }) {
  return message ? <p className="error" role="alert">{message}</p> : null
}

function Bars({ title, columns, series, yMax, label }) {
  const [active, setActive] = useState(null)
  const step = yMax <= 20 ? 5 : yMax <= 50 ? 10 : 25
  const ticks = Array.from({ length: Math.floor(yMax / step) + 1 }, (_, i) => i * step)
  const count = columns.length
  const edge = active === null ? '' : active < 3 ? 'left' : active > count - 4 ? 'right' : ''

  return (
    <figure className="chart">
      <figcaption>
        <h3>{title}</h3>
        {series.length > 1 && (
          <div className="legend">
            {series.map((item) => <span key={item.name}><i style={{ background: item.color }} />{item.name}</span>)}
          </div>
        )}
      </figcaption>
      <div className="plot" role="img" aria-label={label} onMouseLeave={() => setActive(null)}>
        {ticks.map((tick) => (
          <div key={tick} className="gridline" style={{ bottom: `${(tick / yMax) * 100}%` }}><span>{tick}%</span></div>
        ))}
        <div className="columns">
          {columns.map((column, i) => (
            <div key={column.label} className={`column ${active === i ? 'active' : ''}`} onMouseEnter={() => setActive(i)}>
              {column.values.map((value, s) => (
                <i key={s} style={{ height: `${(value / yMax) * 100}%`, background: series[s].color }} />
              ))}
            </div>
          ))}
        </div>
        {active !== null && (
          <div className={`tooltip ${edge}`} style={{ left: `${((active + 0.5) / count) * 100}%` }}>
            <b>{columns[active].label}</b>
            {series.map((item, s) => (
              <span key={item.name}><i style={{ background: item.color }} />{item.name} <em>{columns[active].values[s].toFixed(1)}%</em></span>
            ))}
          </div>
        )}
      </div>
      <div className="xaxis">{columns.map((column) => <span key={column.label}>{column.label}</span>)}</div>
    </figure>
  )
}

function DataTable({ headers, rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr></thead>
        <tbody>
          {rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}
        </tbody>
      </table>
    </div>
  )
}

function CipherSection({ keys, setKeys, plaintext, setPlaintext, result, onEncrypt, busy, error }) {
  const [ciphertext, setCiphertext] = useState('')
  const [decrypted, setDecrypted] = useState(null)
  const [decryptError, setDecryptError] = useState('')
  useEffect(() => { if (result) { setCiphertext(result.ciphertext); setDecrypted(null); setDecryptError('') } }, [result])

  async function decrypt(event) {
    event.preventDefault()
    setDecryptError('')
    setDecrypted(null)
    try {
      setDecrypted((await api('/api/decrypt', { ...keys, ciphertext })).plaintext)
    } catch (failure) {
      setDecryptError(failure.message)
    }
  }

  const stages = result && [
    ['Plaintext', 'Letters A-Z only', inPairs(result.plaintext)],
    ['Padded', result.padded.length - result.plaintext.length === 1 ? 'Added X' : 'Added XA', inPairs(result.padded)],
    ['Stage 1', 'After Vigenere', inPairs(result.after_vigenere)],
    ['Stage 2', 'After Hill: ciphertext', inPairs(result.ciphertext)],
  ]

  return (
    <div className="bento">
      <form className="card span-5" onSubmit={onEncrypt}>
        <h3>Your message and keys</h3>
        <label className="field">
          <span className="field-label">Message</span>
          <textarea rows="5" value={plaintext} onChange={(e) => setPlaintext(e.target.value)} placeholder="Type any message. Only the letters A-Z are encrypted." />
        </label>
        <KeyField label="Vigenere key" value={keys.vigenere_key} onChange={(v) => setKeys({ ...keys, vigenere_key: v })} placeholder="At least 10 letters" />
        <KeyField label="Hill key phrase" value={keys.hill_key} onChange={(v) => setKeys({ ...keys, hill_key: v })} placeholder="At least 10 letters" />
        <button disabled={busy}>{busy ? 'Encrypting...' : 'Encrypt'}</button>
        <ErrorNote message={error} />
      </form>

      <div className="card span-7">
        <div className="card-head">
          <h3>Stage by stage</h3>
          {result && (
            <span className={`badge ${result.decrypted === result.plaintext ? 'good' : 'bad'}`}>
              {result.decrypted === result.plaintext ? 'Decrypts exactly' : 'Decryption mismatch'}
            </span>
          )}
        </div>
        {!result && <p className="empty">The output of each stage appears here after you encrypt.</p>}
        {result && stages.map(([name, note, value]) => (
          <div className="stage" key={name}>
            <div><b>{name}</b><span>{note}</span></div>
            <code>{value}</code>
          </div>
        ))}
      </div>

      <div className="card span-5">
        <h3>Hill matrix from your phrase</h3>
        {!result && <p className="empty">Every letter of the phrase feeds this matrix.</p>}
        {result && (
          <div className="matrices">
            <Matrix title="Key K" rows={result.hill_matrix} />
            <Matrix title="Inverse K⁻¹ mod 26" rows={result.hill_inverse} />
          </div>
        )}
      </div>

      <form className="card span-7" onSubmit={decrypt}>
        <h3>Decrypt a ciphertext</h3>
        <label className="field">
          <span className="field-label">Ciphertext, using the keys entered above</span>
          <textarea rows="3" value={ciphertext} onChange={(e) => setCiphertext(e.target.value)} placeholder="Paste a ciphertext" spellCheck="false" className="mono" />
        </label>
        <button className="secondary">Decrypt</button>
        <ErrorNote message={decryptError} />
        {decrypted !== null && <code className="output">{decrypted}</code>}
      </form>
    </div>
  )
}

function AnalysisSection({ result }) {
  if (!result) return <p className="card empty">Encrypt a message above to compare its letter frequencies with English.</p>

  const { stats, frequencies: f } = result
  const peak = Math.max(...ALPHABET.flatMap((letter) => [f.plaintext[letter], f.ciphertext[letter], f.english[letter]]))
  const yMax = Math.ceil(peak / 5) * 5
  const columnsFor = (text) => ALPHABET.map((letter) => ({ label: letter, values: [text[letter], f.english[letter]] }))

  return (
    <>
      <div className="tiles">
        <Tile label="Plaintext IoC" value={stats.plaintext_ioc.toFixed(4)} note="English is about 0.0667" />
        <Tile label="Ciphertext IoC" value={stats.ciphertext_ioc.toFixed(4)} note="Uniform text is 0.0385" />
        <Tile label="Plaintext chi-squared" value={number(Math.round(stats.plaintext_chi_sq))} note="Low means close to English" />
        <Tile label="Ciphertext chi-squared" value={number(Math.round(stats.ciphertext_chi_sq))} note={`${stats.ciphertext_length} letters analysed`} />
      </div>
      <div className="card charts">
        <Bars title="Plaintext letters against English" yMax={yMax} columns={columnsFor(f.plaintext)}
          series={[{ name: 'Your plaintext', color: BLUE }, { name: 'Expected English', color: AMBER }]}
          label="Bar chart of plaintext letter frequency beside expected English frequency, also available as a table below" />
        <Bars title="Ciphertext letters against English" yMax={yMax} columns={columnsFor(f.ciphertext)}
          series={[{ name: 'Ciphertext', color: BLUE }, { name: 'Expected English', color: AMBER }]}
          label="Bar chart of ciphertext letter frequency beside expected English frequency, also available as a table below" />
        <details>
          <summary>View as table</summary>
          <DataTable headers={['Letter', 'Plaintext %', 'Ciphertext %', 'English %']}
            rows={ALPHABET.map((letter) => [letter, f.plaintext[letter].toFixed(2), f.ciphertext[letter].toFixed(2), f.english[letter].toFixed(2)])} />
        </details>
        <p className="footnote">Short messages give noisy statistics. A few hundred letters show the flattening clearly.</p>
      </div>
    </>
  )
}

function AttackSection({ result }) {
  const [ciphertext, setCiphertext] = useState('')
  const [known, setKnown] = useState('')
  const [outcome, setOutcome] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!result) return
    setCiphertext(result.ciphertext)
    setKnown(result.plaintext.slice(0, result.vigenere_key.length + 21))
    setOutcome(null)
    setError('')
  }, [result])

  async function run(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setOutcome(null)
    try {
      setOutcome(await api('/api/attack', { ciphertext, known_plaintext: known }))
    } catch (failure) {
      setError(failure.message)
    }
    setBusy(false)
  }

  const matchesOriginal = outcome?.success && result?.ciphertext === ciphertext && outcome.recovered_full_plaintext === result.plaintext

  return (
    <div className="bento">
      <form className="card span-5" onSubmit={run}>
        <h3>What the attacker has</h3>
        <label className="field">
          <span className="field-label">Intercepted ciphertext</span>
          <textarea rows="4" value={ciphertext} onChange={(e) => setCiphertext(e.target.value)} placeholder="Encrypt above or paste a ciphertext" spellCheck="false" className="mono" />
        </label>
        <label className="field">
          <span className="field-label">Known plaintext, from the start<span className="count">{letterCount(known)} letters</span></span>
          <textarea rows="3" value={known} onChange={(e) => setKnown(e.target.value)} placeholder="The first letters of the message" spellCheck="false" className="mono" />
        </label>
        {result && (
          <label className="field">
            <span className="field-label">Letters known from your message</span>
            <input type="range" min="0" max={result.plaintext.length} value={Math.min(letterCount(known), result.plaintext.length)}
              onChange={(e) => setKnown(result.plaintext.slice(0, Number(e.target.value)))} />
          </label>
        )}
        <button disabled={busy}>{busy ? 'Searching 157,248 matrices...' : 'Run attack'}</button>
        <p className="footnote">The attacker is not given either key or the key length.</p>
        <ErrorNote message={error} />
      </form>

      <div className="card span-7" aria-live="polite">
        <div className="card-head">
          <h3>Result</h3>
          {outcome && <span className={`badge ${outcome.success ? 'bad' : 'good'}`}>{outcome.success ? 'Cipher broken' : 'Key not found'}</span>}
        </div>
        {!outcome && !busy && <p className="empty">Recovered keys and the full message appear here.</p>}
        {busy && <p className="empty">The Python attack is running.</p>}
        {outcome && !outcome.success && (
          <p className="explain">
            {result?.ciphertext === ciphertext && outcome.known_letters >= result.plaintext.length
              ? `This message is too short to break. Different keys can fit its ${result.plaintext.length} letters, so the real key cannot be identified. Encrypt a message of at least ${result.vigenere_key.length + 21} letters and run the attack again.`
              : `The attack needs at least the key length plus 20 known letters, so it refused to guess with only ${outcome.known_letters}. Provide more known letters and run it again.`}
          </p>
        )}
        {outcome?.success && (
          <>
            <div className="metrics">
              <div><span className="tile-label">Vigenere key</span><code>{outcome.recovered_vigenere_key}</code></div>
              <div><span className="tile-label">Key length</span><code>{outcome.recovered_key_len}</code></div>
              <div><span className="tile-label">Time</span><code>{(outcome.elapsed_seconds * 1000).toFixed(0)} ms</code></div>
              <div><span className="tile-label">Matrices tried</span><code>{number(outcome.matrices_evaluated)}</code></div>
            </div>
            <Matrix title="Recovered Hill matrix" rows={[outcome.recovered_hill_mat.slice(0, 2), outcome.recovered_hill_mat.slice(2)]} />
            <div className="recovered">
              <span className="tile-label">Recovered message{matchesOriginal && <span className="badge good">Matches original</span>}</span>
              <code className="output">{outcome.recovered_full_plaintext}</code>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function MeasurementsSection() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api('/api/results').then(setData).catch((failure) => setError(failure.message)) }, [])

  if (error) return <ErrorNote message={error} />
  if (!data) return <p className="card empty">Loading measurements...</p>

  const { attack, ciphers, frequency, environment } = data
  return (
    <div className="bento">
      <div className="card span-6">
        <Bars title="Attack success by known letters" yMax={100}
          columns={attack.by_known.map((row) => ({ label: String(row.known_chars), values: [row.success_rate] }))}
          series={[{ name: 'Exact recovery', color: BLUE }]}
          label="Bar chart of attack success rate by number of known letters, with values in the table below" />
        <DataTable headers={['Known letters', 'Success', 'Avg time (ms)']}
          rows={attack.by_known.map((row) => [row.known_chars, `${row.success_rate.toFixed(0)}%`, row.avg_time_ms.toFixed(1)])} />
      </div>
      <div className="card span-6">
        <h3>Attack by ciphertext length</h3>
        <p className="footnote">First 25% of each message known, {attack.by_length[0].trials} random trials per row.</p>
        <DataTable headers={['Length', 'Known', 'Success', 'Avg time (ms)']}
          rows={attack.by_length.map((row) => [number(row.length), number(row.known_chars), `${row.success_rate.toFixed(0)}%`, row.avg_time_ms.toFixed(1)])} />
      </div>
      <div className="card span-7">
        <h3>Custom cipher against Shift cipher</h3>
        <p className="footnote">Milliseconds, averaged over 50 runs on Python {environment.python}.</p>
        <DataTable headers={['Letters', 'Custom enc', 'Custom dec', 'Shift enc', 'Shift dec', 'Overhead']}
          rows={ciphers.map((row) => [number(row.length), row.custom_enc_ms.toFixed(3), row.custom_dec_ms.toFixed(3), row.shift_enc_ms.toFixed(3), row.shift_dec_ms.toFixed(3), `${(row.custom_enc_ms / row.shift_enc_ms).toFixed(2)}x`])} />
      </div>
      <div className="card span-5">
        <h3>Letter statistics</h3>
        <p className="footnote">{frequency.samples} random keys, {number(frequency.length)}-letter messages.</p>
        <DataTable headers={['Text', 'Mean IoC']}
          rows={Object.entries(frequency.ciphers).map(([name, row]) => [name, row.ioc.toFixed(4)])} />
      </div>
    </div>
  )
}

export default function App() {
  const [keys, setKeys] = useState({ vigenere_key: '', hill_key: '' })
  const [plaintext, setPlaintext] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.filter((entry) => entry.isIntersecting).forEach((entry) => {
        entry.target.classList.add('in')
        observer.unobserve(entry.target)
      })
    }, { rootMargin: '0px 0px -8% 0px' })
    document.querySelectorAll('.reveal').forEach((element) => observer.observe(element))
    return () => observer.disconnect()
  }, [])

  async function encrypt(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setResult(await api('/api/encrypt', { ...keys, plaintext }))
    } catch (failure) {
      setError(failure.message)
    }
    setBusy(false)
  }

  return (
    <>
      <nav className="nav">
        <div className="wrap nav-inner">
          <a href="#top" className="brand">CT-486 Cipher Lab</a>
          <div className="links">
            <a href="#encrypt">Encrypt</a>
            <a href="#analysis">Analysis</a>
            <a href="#attack">Attack</a>
            <a href="#measurements">Measurements</a>
          </div>
        </div>
      </nav>

      <main className="wrap" id="top">
        <header className="hero reveal">
          <span className="eyebrow">Network and Information Security, Complex Computing Problem</span>
          <h1>A two-stage classical cipher, built and then broken.</h1>
          <p>Enter your own message and keys. Every value on this page is computed by the project's Python code.</p>
          <div className="pipeline" aria-label="Plaintext goes through Vigenere, then Hill, to give ciphertext">
            <span>Plaintext</span><i />
            <span className="step">Vigenere<small>Substitution</small></span><i />
            <span className="step">Hill 2×2<small>Matrix mod 26</small></span><i />
            <span>Ciphertext</span>
          </div>
        </header>

        <Section id="encrypt" index="01" title="Encrypt and decrypt" lead="Letters are grouped in pairs below because the Hill stage works on two letters at a time.">
          <CipherSection keys={keys} setKeys={setKeys} plaintext={plaintext} setPlaintext={setPlaintext} result={result} onEncrypt={encrypt} busy={busy} error={error} />
        </Section>

        <Section id="analysis" index="02" title="Frequency analysis" lead="English has a distinctive letter pattern. A good cipher hides it, so the blue bars should stop following the amber ones.">
          <AnalysisSection result={result} />
        </Section>

        <Section id="attack" index="03" title="Known-plaintext attack" lead="Both stages are linear, so an attacker who knows the start of a message can test every Hill matrix and read off the Vigenere key.">
          <AttackSection result={result} />
        </Section>

        <Section id="measurements" index="04" title="Measured results" lead="Recorded by benchmark.py with random keys and real English text. These are the same figures used in the report.">
          <MeasurementsSection />
        </Section>
      </main>

      <footer className="wrap footer">
        <span>CT-486 Network and Information Security, NED University</span>
        <a href="https://github.com/ameemakhtr/NIS_CCP">Source on GitHub</a>
      </footer>
    </>
  )
}
