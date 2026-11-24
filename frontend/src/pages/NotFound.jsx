import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center">
      <p className="text-gold-400 font-bold text-sm uppercase tracking-wider">404</p>
      <h1 className="font-display text-4xl font-extrabold mt-2">Page not found</h1>
      <p className="text-white/50 mt-2">That page doesn't exist or has moved.</p>
      <Link to="/" className="btn-primary mt-6">
        Take me home
      </Link>
    </div>
  );
}
