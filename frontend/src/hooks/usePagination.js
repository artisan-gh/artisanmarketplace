import { useState } from 'react';

export function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [total, setTotal] = useState(0);

  return {
    page,
    pageSize,
    total,
    setPage,
    setPageSize,
    setTotal,
    reset: () => { setPage(1); setPageSize(initialPageSize); },
  };
}