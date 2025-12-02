import { toast } from 'sonner';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

/**
 * Export payment history for a leader/client as CSV
 */
export async function exportLeaderPayments(leaderId: string, leaderName: string): Promise<void> {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_BASE}/leaders/${leaderId}/payments/export`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to export payment history');
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Extract filename from Content-Disposition header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
            : `${leaderName.replace(/\s+/g, '_')}_Payment_History_${new Date().toISOString().split('T')[0]}.csv`;

        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        toast.success('Payment history exported successfully');
    } catch (error) {
        console.error('Export error:', error);
        toast.error('Failed to export payment history');
        throw error;
    }
}
