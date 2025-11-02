import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Info } from 'lucide-react';

export default function WelcomeAlert() {
  return (
    <Alert className="mb-6">
      <Info className="h-4 w-4" />
      <AlertTitle>Welcome to SchoolCopy Business Manager!</AlertTitle>
      <AlertDescription>
        You're now logged in. To change currency settings, go to <strong>Settings</strong> and update the Currency & Regional Settings section.
      </AlertDescription>
    </Alert>
  );
}
