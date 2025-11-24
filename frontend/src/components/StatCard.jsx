export default function StatCard({ icon, label, value, subtext }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {subtext && <p className="text-sm text-gray-500 mt-1">{subtext}</p>}
        </div>
        <div className="ml-4 text-indigo-600">{icon}</div>
      </div>
    </div>
  );
}
