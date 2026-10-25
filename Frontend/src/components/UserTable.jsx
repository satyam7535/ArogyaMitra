export const UserTable = ({ columns, data, actions }) => {
    return (
      <div className="overflow-x-auto bg-white rounded-lg shadow border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {col.label}
                </th>
              ))}
               {actions && <th scope="col" className="relative px-6 py-3"><span className="sr-only">Actions</span></th>}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, rowIndex) => (
              <tr key={row.id || rowIndex} className="hover:bg-gray-50 transition-colors">
                {columns.map((col) => (
                  <td key={`${row.id}-${col.key}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
                 {actions && (
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {actions(row)}
                    </td>
                 )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };
