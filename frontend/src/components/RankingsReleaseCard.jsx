import { useEffect, useState } from 'react';
import { Eye, EyeOff, Trophy, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { siteService } from '@/services/site.service';
import { DEFAULT_RELEASE_MESSAGE } from '@/hooks/useRankingsRelease';

/**
 * Rankings release switch. While OFF, the public Rankings, University Rankings
 * and field pages show a "coming soon" message instead of any rankings — so
 * nobody can game the leaderboard by watching interim results while
 * registration is open. Turn it ON to publish.
 *
 * Rendered on the admin dashboard (where admins land) as well as under
 * Settings, because staff accounts can preview rankings even while they are
 * hidden — so without an explicit indicator an admin has no way to tell that
 * the public is seeing an empty page.
 *
 * Requires the `manage_site` permission; callers must gate on it.
 */
export function RankingsReleaseCard({ className = '' }) {
  const [released, setReleased] = useState(false);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadFailed, setLoadFailed] = useState(false);

  useEffect(() => {
    siteService
      .get('rankings')
      .then((res) => {
        const data = res?.data || {};
        setReleased(!!data.released);
        setMessage(data.message || '');
        setLoadFailed(false);
      })
      // The PUT below replaces the WHOLE document, so saving from a baseline we
      // failed to read would overwrite a custom message with the default. Block
      // writing instead.
      .catch(() => setLoadFailed(true))
      .finally(() => setLoading(false));
  }, []);

  const save = async (nextReleased) => {
    setSaving(true);
    try {
      await siteService.update('rankings', {
        released: nextReleased,
        message: message.trim() || DEFAULT_RELEASE_MESSAGE,
      });
      setReleased(nextReleased);
      toast.success(nextReleased ? 'Rankings are now public.' : 'Rankings are hidden.');
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not update.');
    } finally {
      setSaving(false);
    }
  };

  const blocked = loading || saving || loadFailed;

  return (
    <div className={`card p-6 ${className}`}>
      <div className="flex items-start gap-3">
        <span className="w-9 h-9 shrink-0 rounded-lg bg-gold-400/15 grid place-content-center text-gold-400">
          <Trophy className="w-4 h-4" />
        </span>
        <div>
          <h2 className="font-display text-lg font-bold">Rankings visibility</h2>
          <p className="text-sm text-white/55 mt-0.5">
            Controls whether the public can see the leaderboard. Staff always see it.
          </p>
        </div>
      </div>

      {loadFailed && (
        <p className="mt-4 flex items-start gap-2 rounded-lg border border-amber-500/25 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-px" />
          Could not load the current setting, so changes are disabled — saving now would overwrite
          your “coming soon” message. Reload to try again.
        </p>
      )}

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-ink-900/40 px-4 py-3">
        <div className="flex items-center gap-2 text-sm">
          {released ? (
            <Eye className="w-4 h-4 text-emerald-300" />
          ) : (
            <EyeOff className="w-4 h-4 text-white/50" />
          )}
          <span className={released ? 'text-emerald-300' : 'text-white/70'}>
            {loading
              ? 'Loading…'
              : loadFailed
              ? 'Unknown'
              : released
              ? 'Rankings are PUBLIC'
              : 'Rankings are HIDDEN from the public'}
          </span>
        </div>
        <button
          type="button"
          disabled={blocked}
          onClick={() => save(!released)}
          className={released ? 'btn-ghost text-xs' : 'btn-primary text-xs'}
        >
          {saving ? 'Saving…' : released ? 'Hide rankings' : 'Publish rankings'}
        </button>
      </div>

      <div className="mt-4">
        <label className="field-label">“Coming soon” message (shown while hidden)</label>
        <textarea
          className="input min-h-[70px]"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={DEFAULT_RELEASE_MESSAGE}
        />
        <div className="mt-2 flex justify-end">
          <button
            type="button"
            disabled={blocked}
            onClick={() => save(released)}
            className="btn-ghost text-xs"
          >
            Save message
          </button>
        </div>
      </div>
    </div>
  );
}
