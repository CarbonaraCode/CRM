import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import DataTable from './DataTable';

const sampleData = [
  { id: 1, name: 'Alpha', email: 'a@test.com' },
  { id: 2, name: 'Beta', email: 'b@test.com' },
];

const columns = [
  { header: 'Nome', accessor: 'name' },
  { header: 'Email', accessor: 'email' },
];

describe('DataTable', () => {
  it('renders rows and filters by search', () => {
    render(<DataTable title="Test Table" columns={columns} data={sampleData} onAdd={() => {}} />);

    expect(screen.getByText('Test Table')).toBeInTheDocument();
    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();

    const search = screen.getByPlaceholderText('Cerca...');
    fireEvent.change(search, { target: { value: 'Alpha' } });

    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.queryByText('Beta')).not.toBeInTheDocument();
  });
});
