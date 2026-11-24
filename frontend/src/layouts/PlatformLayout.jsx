import { Outlet } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

/**
 * Layout for the public platform surfaces, including the home page at "/".
 * Carries the primary navigation (Rankings, Fields, Universities, …) plus the
 * join / sign-in controls. This is the only public layout — there is a single
 * landing page at "/".
 */
export function PlatformLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
