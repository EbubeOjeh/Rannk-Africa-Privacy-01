import { useState } from 'react';
import { Send, Mail } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { contactService } from '@/services/contact.service';

const empty = {
  sender_name: '',
  sender_email: '',
  sender_organization: '',
  sender_role: '',
  subject: '',
  message: '',
};

export function ContactStudentForm({ studentId, studentName }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(empty);
  const [sending, setSending] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await contactService.send(studentId, form);
      toast.success('Message delivered. The student will receive it privately.');
      setForm(empty);
      setOpen(false);
    } catch (err) {
      toast.error(err?.response?.data?.error?.message || 'Could not send message.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wider text-cream/50">For employers / recruiters</p>
          <h2 className="font-display text-xl font-bold mt-1">Contact this student</h2>
          <p className="text-sm text-cream/60 mt-1">
            Your message is forwarded to {studentName.split(' ')[0]}'s private email. Their
            address is never shared.
          </p>
        </div>
        <button onClick={() => setOpen((v) => !v)} className="btn-primary">
          <Mail className="w-4 h-4" /> {open ? 'Close' : 'Send a message'}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.form
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            onSubmit={submit}
            className="mt-5 grid gap-3 overflow-hidden"
          >
            <div className="grid sm:grid-cols-2 gap-3">
              <Field label="Your name" required>
                <input
                  className="input"
                  value={form.sender_name}
                  onChange={(e) => setForm({ ...form, sender_name: e.target.value })}
                  required
                  minLength={2}
                />
              </Field>
              <Field label="Your email" required>
                <input
                  type="email"
                  className="input"
                  value={form.sender_email}
                  onChange={(e) => setForm({ ...form, sender_email: e.target.value })}
                  required
                />
              </Field>
              <Field label="Organization">
                <input
                  className="input"
                  value={form.sender_organization}
                  onChange={(e) => setForm({ ...form, sender_organization: e.target.value })}
                />
              </Field>
              <Field label="Your role">
                <input
                  className="input"
                  placeholder="Recruiter, Hiring Manager, …"
                  value={form.sender_role}
                  onChange={(e) => setForm({ ...form, sender_role: e.target.value })}
                />
              </Field>
            </div>
            <Field label="Subject" required>
              <input
                className="input"
                value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                required
                minLength={4}
              />
            </Field>
            <Field label="Message" required>
              <textarea
                className="input min-h-[120px]"
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                required
                minLength={10}
              />
            </Field>
            <div className="flex items-center justify-end gap-2">
              <button type="button" className="btn-ghost" onClick={() => setForm(empty)}>
                Clear
              </button>
              <button type="submit" disabled={sending} className="btn-primary">
                <Send className="w-4 h-4" /> {sending ? 'Sending…' : 'Send via relay'}
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}

function Field({ label, required, children }) {
  return (
    <label className="block">
      <span className="field-label">
        {label} {required && <span className="text-gold-400">*</span>}
      </span>
      {children}
    </label>
  );
}
