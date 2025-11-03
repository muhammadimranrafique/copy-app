import { Card, CardContent } from '@/components/ui/card';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  trend?: string;
  colorClass?: string;
}

export default function StatCard({ title, value, icon: Icon, trend, colorClass = 'text-primary' }: StatCardProps) {
  return (
    <Card className="card-hover">
      <CardContent className="p-4 sm:p-6">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm font-medium text-muted-foreground truncate">{title}</p>
            <p className="text-xl sm:text-2xl font-bold mt-1 sm:mt-2 truncate">{value}</p>
            {trend && <p className="text-xs text-muted-foreground mt-1 truncate">{trend}</p>}
          </div>
          <div className={`p-2 sm:p-3 rounded-full bg-primary/10 ${colorClass} flex-shrink-0`}>
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
