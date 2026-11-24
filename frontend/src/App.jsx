import ExitQuestionnaire from '@/components/ExitQuestionnaire';
import { AppRoutes } from './routes';
import { ScrollManager } from '@/components/ScrollManager';

export default function App() {
  return (
    <>
      <ScrollManager />
      <AppRoutes />
      <ExitQuestionnaire />
    </>
  );
}
