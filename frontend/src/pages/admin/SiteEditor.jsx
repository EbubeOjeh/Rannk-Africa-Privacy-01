import { useEffect, useState } from 'react';
import {
  Save,
  RotateCcw,
  Plus,
  Trash2,
  ArrowUp,
  ArrowDown,
  ExternalLink,
  Search,
  Check,
  ChevronDown,
  MousePointerClick,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { siteService } from '@/services/site.service';
import {
  PAGES,
  PAGE_DEFAULTS,
  STORAGE_KEYS,
  EDIT_SCHEMA,
  mergeContent,
  getPath,
  setPath,
} from '@/content/pageContent';
import { ICON_NAMES, iconFor, ACCENTS, ACCENT_NAMES, accentFor } from '@/content/visuals';
import { Loader } from '@/components/Loader';
import { PageGuide } from '@/components/PageGuide';
import { EditContext } from '@/content/EditContext';

// Page components rendered in the live preview.
import Platform from '@/pages/Platform';
import About from '@/pages/About';
import OpportunityPortal from '@/pages/Opportunities';
import Rankings from '@/pages/Rankings';
import Universities from '@/pages/Universities';
import Fields from '@/pages/Fields';
import Team from '@/pages/Team';
import Contact from '@/pages/Contact';

const PREVIEW_COMPONENTS = {
  platform: Platform,
  about: About,
  opportunities: OpportunityPortal,
  rankings: Rankings,
  universities: Universities,
  fields: Fields,
  team: Team,
  contact: Contact,
};

const clone = (o) => JSON.parse(JSON.stringify(o));
const newId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `id-${Date.now()}-${Math.round(Math.random() * 1e6)}`;

const scrollToSection = (id) => {
  const el = document.getElementById(`edit-section-${id}`);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

/* ---------------------------------------------------------------- shared ---- */

function Field({ label, value, onChange, textarea, rows = 3, placeholder }) {
  return (
    <div>
      <label className="field-label">{label}</label>
      {textarea ? (
        <textarea
          className="input"
          rows={rows}
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
        />
      ) : (
        <input
          className="input"
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
        />
      )}
    </div>
  );
}

function Section({ id, title, desc, action, active, children }) {
  return (
    <section
      id={id ? `edit-section-${id}` : undefined}
      className={`card p-5 sm:p-6 scroll-mt-24 transition ${active ? 'ring-2 ring-gold-400' : ''}`}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-lg font-bold text-white">{title}</h2>
          {desc && <p className="text-xs text-cream/50 mt-0.5">{desc}</p>}
        </div>
        {action}
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function IconPicker({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const Current = iconFor(value);
  const names = ICON_NAMES.filter((n) => n.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="relative">
      <label className="field-label">Icon</label>
      <button type="button" onClick={() => setOpen((v) => !v)} className="input flex items-center justify-between">
        <span className="flex items-center gap-2">
          <Current className="w-4 h-4 text-gold-300" /> {value || 'Sparkles'}
        </span>
        <ChevronDown className="w-4 h-4 text-cream/40" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute z-40 mt-1 w-72 max-w-[80vw] rounded-xl border border-cream/10 bg-ink-850 shadow-xl p-3">
            <div className="flex items-center gap-2 mb-2 px-1">
              <Search className="w-4 h-4 text-cream/40" />
              <input
                autoFocus
                className="bg-transparent text-sm text-white outline-none w-full"
                placeholder="Search icons…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-6 gap-1 max-h-56 overflow-y-auto scrollbar-thin">
              {names.map((n) => {
                const I = iconFor(n);
                const active = n === value;
                return (
                  <button
                    key={n}
                    type="button"
                    title={n}
                    onClick={() => {
                      onChange(n);
                      setOpen(false);
                    }}
                    className={`h-9 grid place-content-center rounded-lg ${
                      active ? 'bg-gold-400/20 text-gold-300' : 'text-cream/70 hover:bg-cream/10'
                    }`}
                  >
                    <I className="w-4 h-4" />
                  </button>
                );
              })}
              {names.length === 0 && <p className="col-span-6 text-xs text-cream/40 py-3 text-center">No icons match.</p>}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function AccentPicker({ value, onChange }) {
  return (
    <div>
      <label className="field-label">Accent colour</label>
      <div className="flex flex-wrap gap-2">
        {ACCENT_NAMES.map((n) => {
          const a = ACCENTS[n];
          const active = n === value;
          return (
            <button
              key={n}
              type="button"
              title={a.label}
              onClick={() => onChange(n)}
              className={`w-8 h-8 rounded-full ${a.swatch} grid place-content-center ring-2 transition ${
                active ? 'ring-white' : 'ring-transparent hover:ring-white/40'
              }`}
            >
              {active && <Check className="w-4 h-4 text-black/80" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function CardShell({ index, total, onMove, onRemove, accent, icon, title, children }) {
  const a = accentFor(accent);
  const I = iconFor(icon);
  return (
    <div className="rounded-xl border border-cream/10 bg-ink-900/40 p-4">
      <div className="flex items-center gap-3 mb-3">
        {icon !== undefined && (
          <div className={`w-9 h-9 rounded-lg ${a.chipBg} grid place-content-center ${a.chipText} shrink-0`}>
            <I className="w-4 h-4" />
          </div>
        )}
        <span className="text-sm font-medium text-white truncate flex-1">{title || 'Untitled'}</span>
        <div className="flex items-center gap-1 shrink-0">
          <button type="button" disabled={index === 0} onClick={() => onMove(-1)} className="btn-ghost h-8 w-8 p-0 disabled:opacity-30" title="Move up">
            <ArrowUp className="w-4 h-4" />
          </button>
          <button type="button" disabled={index === total - 1} onClick={() => onMove(1)} className="btn-ghost h-8 w-8 p-0 disabled:opacity-30" title="Move down">
            <ArrowDown className="w-4 h-4" />
          </button>
          <button type="button" onClick={onRemove} className="btn-ghost h-8 w-8 p-0" title="Remove">
            <Trash2 className="w-4 h-4 text-rose-300" />
          </button>
        </div>
      </div>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

function EmptyHint({ children }) {
  return (
    <p className="text-xs text-cream/40 border border-dashed border-cream/15 rounded-lg py-4 text-center">{children}</p>
  );
}

/* ------------------------------------------------------- schema-driven form -- */

function ListEditor({ list, content, onChange }) {
  const items = getPath(content, list.path) || [];
  const write = (next) => onChange(setPath(content, list.path, next));
  const patch = (i, k, v) => write(items.map((it, idx) => (idx === i ? { ...it, [k]: v } : it)));
  const move = (i, dir) => {
    const a = [...items];
    const j = i + dir;
    if (j < 0 || j >= a.length) return;
    [a[i], a[j]] = [a[j], a[i]];
    write(a);
  };
  const remove = (i) => write(items.filter((_, idx) => idx !== i));
  const add = () => write([...items, { ...list.blank }]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-cream/50">{list.label}</p>
        <button type="button" onClick={add} className="btn-primary text-xs">
          <Plus className="w-4 h-4" /> Add
        </button>
      </div>
      {items.length === 0 && <EmptyHint>Nothing yet — add one above.</EmptyHint>}
      {items.map((it, i) => (
        <CardShell
          key={i}
          index={i}
          total={items.length}
          title={it[list.itemFields[0].key]}
          onMove={(dir) => move(i, dir)}
          onRemove={() => remove(i)}
        >
          {list.itemFields.map((f) => (
            <Field
              key={f.key}
              label={f.label}
              textarea={f.textarea}
              value={it[f.key]}
              onChange={(v) => patch(i, f.key, v)}
            />
          ))}
        </CardShell>
      ))}
    </div>
  );
}

function SchemaForm({ pageKey, content, onChange, activeSection }) {
  const schema = EDIT_SCHEMA[pageKey] || [];
  return (
    <div className="space-y-6">
      {schema.map((section) => (
        <Section key={section.id} id={section.id} title={section.title} active={activeSection === section.id}>
          {section.fields?.map((f) => (
            <Field
              key={f.path}
              label={f.label}
              textarea={f.textarea}
              rows={f.rows}
              value={getPath(content, f.path)}
              onChange={(v) => onChange(setPath(content, f.path, v))}
            />
          ))}
          {section.list && <ListEditor list={section.list} content={content} onChange={onChange} />}
        </Section>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------ landing form -- */

/* ---------------------------------------------------------------- preview ---- */

function Preview({ pageKey, draft, activeSection, onFocus }) {
  const Comp = PREVIEW_COMPONENTS[pageKey];
  return (
    <EditContext.Provider value={{ page: pageKey, draft, activeSection, onFocus }}>
      {/* Capture-prevent default so links in the preview never navigate away. */}
      <div
        onClickCapture={(e) => e.preventDefault()}
        className="relative overflow-auto rounded-xl border border-cream/10 bg-ink-950 h-[calc(100vh-11rem)]"
      >
        <div className="origin-top-left scale-[0.62] w-[161%]">{Comp ? <Comp /> : null}</div>
      </div>
    </EditContext.Provider>
  );
}

/* ------------------------------------------------------------------ editor --- */

export default function SiteEditor() {
  const [activeKey, setActiveKey] = useState('landing');
  const [drafts, setDrafts] = useState({});
  const [savedJson, setSavedJson] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeSection, setActiveSection] = useState(null);
  // On phones the form and preview don't fit side-by-side, so they toggle.
  const [mobileTab, setMobileTab] = useState('edit');

  const activePage = PAGES.find((p) => p.key === activeKey);
  const draft = drafts[activeKey];
  const dirty = draft && JSON.stringify(draft) !== savedJson[activeKey];

  useEffect(() => {
    if (drafts[activeKey]) return;
    setLoading(true);
    siteService
      .get(STORAGE_KEYS[activeKey])
      .then((res) => {
        const data = res?.data && typeof res.data === 'object' ? res.data : {};
        const merged = mergeContent(PAGE_DEFAULTS[activeKey], data);
        setDrafts((d) => ({ ...d, [activeKey]: merged }));
        setSavedJson((s) => ({ ...s, [activeKey]: JSON.stringify(merged) }));
      })
      .catch(() => {
        const merged = mergeContent(PAGE_DEFAULTS[activeKey], {});
        setDrafts((d) => ({ ...d, [activeKey]: merged }));
        setSavedJson((s) => ({ ...s, [activeKey]: JSON.stringify(merged) }));
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeKey]);

  const setDraft = (next) => setDrafts((d) => ({ ...d, [activeKey]: next }));

  const onFocus = (id) => {
    setActiveSection(id);
    // On mobile, jump from the preview back to the fields for this section.
    setMobileTab('edit');
    requestAnimationFrame(() => requestAnimationFrame(() => scrollToSection(id)));
  };

  const selectPage = (key) => {
    setActiveKey(key);
    setActiveSection(null);
  };

  const save = async () => {
    setSaving(true);
    try {
      await siteService.update(STORAGE_KEYS[activeKey], draft);
      setSavedJson((s) => ({ ...s, [activeKey]: JSON.stringify(draft) }));
      toast.success('Saved — changes are live.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not save changes.');
    } finally {
      setSaving(false);
    }
  };

  const reset = () => {
    if (!confirm(`Reset “${activePage.label}” back to the original defaults? (Only saved when you click Save.)`)) return;
    setDraft(clone(PAGE_DEFAULTS[activeKey]));
  };

  return (
    <div className="pb-6">
      <PageGuide
        id="site-editor"
        className="mb-6"
        title="Editing the public website"
        steps={[
          'Pick a page from the selector, then click any highlighted block in the preview to edit its text.',
          'Changes go live for visitors as soon as you save.',
          'The “How it works” scoring breakdown on the home page is fixed in code, because it must match the scoring engine.',
        ]}
      />
      {/* Action bar */}
      <div className="sticky top-0 z-20 -mx-4 lg:-mx-8 px-4 lg:px-8 py-3 bg-ink-950/90 backdrop-blur border-b border-cream/10 mb-5">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <div>
              <h1 className="font-display text-xl font-bold">Website</h1>
              <p className="text-xs text-cream/50">
                Editing <span className="text-gold-300">{activePage.label}</span>
                <span className="text-cream/30"> · {activePage.path}</span> · {dirty ? 'unsaved changes' : 'all saved'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={activeKey}
              onChange={(e) => selectPage(e.target.value)}
              className="input py-1.5 text-sm w-auto"
              title="Choose a page to edit"
            >
              {PAGES.map((p) => (
                <option key={p.key} value={p.key}>
                  {p.label} ({p.path})
                </option>
              ))}
            </select>
            <a href={activePage.path} target="_blank" rel="noreferrer" className="btn-ghost text-xs">
              <ExternalLink className="w-4 h-4" /> View live
            </a>
            <button onClick={reset} className="btn-ghost text-xs" title="Reset this page to defaults">
              <RotateCcw className="w-4 h-4" /> Reset
            </button>
            <button onClick={save} disabled={saving || !dirty} className="btn-primary text-xs">
              <Save className="w-4 h-4" /> {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </div>
      </div>

      {loading || !draft ? (
        <Loader />
      ) : (
        <>
          {/* Mobile-only Edit / Preview toggle (side-by-side on desktop). */}
          <div className="lg:hidden mb-4 grid grid-cols-2 gap-1 rounded-lg border border-cream/10 bg-ink-900/50 p-1 text-sm">
            <button
              onClick={() => setMobileTab('edit')}
              className={`rounded-md py-1.5 font-medium transition ${mobileTab === 'edit' ? 'bg-gold-400/15 text-gold-300' : 'text-cream/60'}`}
            >
              Edit fields
            </button>
            <button
              onClick={() => setMobileTab('preview')}
              className={`rounded-md py-1.5 font-medium transition ${mobileTab === 'preview' ? 'bg-gold-400/15 text-gold-300' : 'text-cream/60'}`}
            >
              Preview
            </button>
          </div>

          <div className="grid lg:grid-cols-[minmax(0,380px)_1fr] gap-6 items-start">
            {/* Form */}
            <div
              className={`min-w-0 lg:max-h-[calc(100vh-9rem)] lg:overflow-y-auto scrollbar-thin pr-1 -mr-1 ${
                mobileTab === 'preview' ? 'hidden lg:block' : 'block'
              }`}
            >
              <SchemaForm pageKey={activeKey} content={draft} onChange={setDraft} activeSection={activeSection} />
            </div>

            {/* Live preview */}
            <div
              className={`lg:sticky lg:top-24 min-w-0 ${mobileTab === 'edit' ? 'hidden lg:block' : 'block'}`}
            >
              <p className="text-xs text-cream/50 mb-2 inline-flex items-center gap-1.5">
                <MousePointerClick className="w-3.5 h-3.5 text-gold-400" /> Live preview — click any section to edit it
              </p>
              <Preview pageKey={activeKey} draft={draft} activeSection={activeSection} onFocus={onFocus} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
