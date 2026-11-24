import { useEffect, useState } from 'react';
import { Ban, Check, Plus, Shield, Trash2, UserPlus, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import { teamService } from '@/services/team.service';
import { Loader } from '@/components/Loader';
import { useAuth } from '@/hooks/useAuth';

function initials(name = '') {
  return name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('') || 'U';
}

export default function Team() {
  const { user } = useAuth();
  const [tab, setTab] = useState('members');
  const [members, setMembers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([teamService.list(), teamService.listRoles(), teamService.permissions()])
      .then(([m, r, p]) => {
        setMembers(m);
        setRoles(r);
        setCatalog(p);
      })
      .catch(() => toast.error('Could not load the team.'))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  if (loading) return <Loader />;

  return (
    <div>
      <h1 className="font-display text-2xl font-bold">Team</h1>
      <p className="text-sm text-cream/60 mt-1">Manage staff accounts and the roles that grant their access.</p>

      <div className="mt-5 flex items-center gap-2">
        <TabBtn active={tab === 'members'} onClick={() => setTab('members')} icon={Users}>
          Members ({members.length})
        </TabBtn>
        <TabBtn active={tab === 'roles'} onClick={() => setTab('roles')} icon={Shield}>
          Roles ({roles.length})
        </TabBtn>
      </div>

      {tab === 'members' ? (
        <Members members={members} roles={roles} me={user} reload={load} />
      ) : (
        <RolesManager roles={roles} catalog={catalog} reload={load} />
      )}
    </div>
  );
}

function TabBtn({ active, onClick, icon: Icon, children }) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-colors ${
        active ? 'bg-gold-400/15 text-gold-300 border-gold-400/30' : 'border-cream/10 text-cream/70 hover:bg-cream/5'
      }`}
    >
      <Icon className="w-4 h-4" /> {children}
    </button>
  );
}

// --------------------------------------------------------------------------- //
function Members({ members, roles, me, reload }) {
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', role_id: '', title: '' });
  const [busy, setBusy] = useState(false);

  const create = async (e) => {
    e.preventDefault();
    if (!form.role_id) return toast.error('Pick a role for the new member.');
    setBusy(true);
    try {
      await teamService.create({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        role_id: form.role_id,
        title: form.title.trim() || undefined,
      });
      toast.success('Team member added. Temporary password: rankpass');
      setForm({ name: '', email: '', role_id: '', title: '' });
      setAdding(false);
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not add member.');
    } finally {
      setBusy(false);
    }
  };

  const setRole = async (m, role_id) => {
    try {
      await teamService.update(m.id, { role_id });
      toast.success('Role updated.');
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Update failed.');
    }
  };

  const toggleBlock = async (m) => {
    try {
      await teamService.update(m.id, { is_active: !m.is_active });
      toast.success(m.is_active ? 'Member blocked.' : 'Member unblocked.');
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Update failed.');
    }
  };

  const remove = async (m) => {
    if (!confirm(`Remove ${m.name}? This permanently deletes their account.`)) return;
    try {
      await teamService.remove(m.id);
      toast.success('Member removed.');
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Delete failed.');
    }
  };

  return (
    <div className="mt-5">
      <div className="flex justify-end mb-3">
        <button onClick={() => setAdding((v) => !v)} className="btn-primary">
          <UserPlus className="w-4 h-4" /> Add member
        </button>
      </div>

      {adding && (
        <form onSubmit={create} className="card p-5 mb-4 grid sm:grid-cols-2 gap-3">
          <div>
            <label className="field-label">Name</label>
            <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="First name" required />
          </div>
          <div>
            <label className="field-label">Email (@rankafrica.org)</label>
            <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="name@rankafrica.org" required />
          </div>
          <div>
            <label className="field-label">Title (optional)</label>
            <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Operations Lead" />
          </div>
          <div>
            <label className="field-label">Role</label>
            <select className="input" value={form.role_id} onChange={(e) => setForm({ ...form, role_id: e.target.value })} required>
              <option value="">Select a role…</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>{r.name}</option>
              ))}
            </select>
          </div>
          <div className="sm:col-span-2 flex gap-2">
            <button type="submit" disabled={busy} className="btn-primary">
              <Plus className="w-4 h-4" /> {busy ? 'Adding…' : 'Add member'}
            </button>
            <button type="button" onClick={() => setAdding(false)} className="btn-ghost">Cancel</button>
          </div>
          <p className="sm:col-span-2 text-xs text-cream/50">
            New members sign in with the temporary password <span className="text-gold-300">rankpass</span> and must change it on first login.
          </p>
        </form>
      )}

      <div className="card divide-y divide-cream/5">
        {members.map((m) => {
          const isAdmin = m.role === 'super_admin';
          const isSelf = m.id === me?.id;
          return (
            <div key={m.id} className="p-4 flex flex-wrap items-center gap-3">
              <div className="w-10 h-10 rounded-full overflow-hidden bg-gold-400/15 grid place-content-center text-sm font-bold text-gold-300 shrink-0">
                {m.avatar_url ? <img src={m.avatar_url} alt={m.name} className="w-full h-full object-cover" /> : initials(m.name)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{m.name}</span>
                  {!m.is_active && <span className="pill-danger">Blocked</span>}
                  {m.must_change_password && <span className="pill-pending">Pending first login</span>}
                </div>
                <div className="text-xs text-cream/50 truncate">{m.email}</div>
              </div>

              {isAdmin ? (
                <span className="pill bg-gold-400/15 text-gold-300">Admin · full access</span>
              ) : (
                <select
                  value={m.company_role_id || ''}
                  onChange={(e) => setRole(m, e.target.value)}
                  className="input w-auto py-1.5 text-sm"
                  title="Assign role"
                >
                  {roles.map((r) => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              )}

              {!isAdmin && !isSelf && (
                <div className="flex items-center gap-1">
                  <button onClick={() => toggleBlock(m)} className="btn-ghost h-8 w-8 p-0" title={m.is_active ? 'Block' : 'Unblock'}>
                    {m.is_active ? <Ban className="w-4 h-4 text-rose-300" /> : <Check className="w-4 h-4 text-emerald-300" />}
                  </button>
                  <button onClick={() => remove(m)} className="btn-ghost h-8 w-8 p-0" title="Delete">
                    <Trash2 className="w-4 h-4 text-rose-300" />
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// --------------------------------------------------------------------------- //
function RolesManager({ roles, catalog, reload }) {
  const [creating, setCreating] = useState(false);
  const [draft, setDraft] = useState({ name: '', description: '', permissions: [] });
  const [busy, setBusy] = useState(false);

  const toggle = (set, key) =>
    set.includes(key) ? set.filter((k) => k !== key) : [...set, key];

  const createRole = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await teamService.createRole({
        name: draft.name.trim(),
        description: draft.description.trim() || undefined,
        permissions: draft.permissions,
      });
      toast.success('Role created.');
      setDraft({ name: '', description: '', permissions: [] });
      setCreating(false);
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not create role.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mt-5">
      <div className="flex justify-end mb-3">
        <button onClick={() => setCreating((v) => !v)} className="btn-primary">
          <Plus className="w-4 h-4" /> New role
        </button>
      </div>

      {creating && (
        <form onSubmit={createRole} className="card p-5 mb-4 space-y-3">
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="field-label">Role name</label>
              <input className="input" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} placeholder="e.g. Partnerships Lead" required />
            </div>
            <div>
              <label className="field-label">Description</label>
              <input className="input" value={draft.description} onChange={(e) => setDraft({ ...draft, description: e.target.value })} placeholder="Optional" />
            </div>
          </div>
          <div>
            <label className="field-label">Permissions</label>
            <div className="grid sm:grid-cols-2 gap-2 mt-1">
              {catalog.map((p) => (
                <label key={p.key} className="flex items-start gap-2 p-2 rounded-lg border border-cream/10 hover:bg-cream/5 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5 accent-gold-400"
                    checked={draft.permissions.includes(p.key)}
                    onChange={() => setDraft({ ...draft, permissions: toggle(draft.permissions, p.key) })}
                  />
                  <span>
                    <span className="text-sm text-white">{p.label}</span>
                    <span className="block text-[11px] text-cream/50">{p.description}</span>
                  </span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={busy} className="btn-primary">{busy ? 'Creating…' : 'Create role'}</button>
            <button type="button" onClick={() => setCreating(false)} className="btn-ghost">Cancel</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {roles.map((r) => (
          <RoleCard key={r.id} role={r} catalog={catalog} reload={reload} />
        ))}
      </div>
    </div>
  );
}

function RoleCard({ role, catalog, reload }) {
  const [perms, setPerms] = useState(role.permissions || []);
  const [busy, setBusy] = useState(false);
  const dirty = JSON.stringify([...perms].sort()) !== JSON.stringify([...(role.permissions || [])].sort());

  const toggle = (key) => setPerms((p) => (p.includes(key) ? p.filter((k) => k !== key) : [...p, key]));

  const save = async () => {
    setBusy(true);
    try {
      await teamService.updateRole(role.id, { permissions: perms });
      toast.success('Role updated.');
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Update failed.');
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (!confirm(`Delete the "${role.name}" role?`)) return;
    try {
      await teamService.removeRole(role.id);
      toast.success('Role deleted.');
      reload();
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Delete failed.');
    }
  };

  return (
    <div className="card p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white">{role.name}</h3>
            {role.is_system && <span className="pill bg-cream/10 text-cream/60">System</span>}
            <span className="text-xs text-cream/50">{role.member_count} member{role.member_count === 1 ? '' : 's'}</span>
          </div>
          {role.description && <p className="text-xs text-cream/50 mt-0.5">{role.description}</p>}
        </div>
        {!role.is_system && (
          <button onClick={remove} className="btn-ghost h-8 w-8 p-0" title="Delete role">
            <Trash2 className="w-4 h-4 text-rose-300" />
          </button>
        )}
      </div>

      <div className="grid sm:grid-cols-2 gap-2 mt-3">
        {catalog.map((p) => (
          <label key={p.key} className="flex items-start gap-2 p-2 rounded-lg border border-cream/10 hover:bg-cream/5 cursor-pointer">
            <input type="checkbox" className="mt-0.5 accent-gold-400" checked={perms.includes(p.key)} onChange={() => toggle(p.key)} />
            <span>
              <span className="text-sm text-white">{p.label}</span>
              <span className="block text-[11px] text-cream/50">{p.description}</span>
            </span>
          </label>
        ))}
      </div>

      {dirty && (
        <div className="mt-3">
          <button onClick={save} disabled={busy} className="btn-primary">{busy ? 'Saving…' : 'Save permissions'}</button>
        </div>
      )}
    </div>
  );
}
