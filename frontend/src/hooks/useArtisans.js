import { useReducer, useEffect, useCallback, useRef } from 'react';
import { getArtisans } from '../api/artisansAPI';

// ─── State ───────────────────────────────────────────────────
const initialState = {
  artisans: [],
  loading: true,
  pagination: { count: 0, next: null, previous: null },
};

function reducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true };
    case 'FETCH_SUCCESS':
      return {
        ...state,
        artisans: action.payload.results || [],
        pagination: {
          count: action.payload.count || 0,
          next: action.payload.next || null,
          previous: action.payload.previous || null,
        },
        loading: false,
      };
    case 'FETCH_MORE':
      return {
        ...state,
        artisans: [...state.artisans, ...(action.payload.results || [])],
        pagination: {
          count: action.payload.count || state.pagination.count,
          next: action.payload.next || null,
          previous: action.payload.previous || null,
        },
        loading: false,
      };
    case 'FETCH_FAIL':
      return { ...state, loading: false };
    default:
      return state;
  }
}

// ─── Hook ────────────────────────────────────────────────────
export function useArtisans(filters) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const isMounted = useRef(true);

  useEffect(() => {
    return () => { isMounted.current = false; };
  }, []);

  const fetchArtisans = useCallback(async (pageUrl = null) => {
    if (!isMounted.current) return;
    dispatch({ type: 'FETCH_START' });

    try {
      const params = { ...filters };
      Object.keys(params).forEach((key) => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      let data;
      if (pageUrl) {
        const response = await fetch(pageUrl);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        data = await response.json();
      } else {
        data = await getArtisans(params);
      }

      if (!isMounted.current) return;
      dispatch({
        type: pageUrl ? 'FETCH_MORE' : 'FETCH_SUCCESS',
        payload: data,
      });
    } catch (error) {
      console.error('Failed to fetch artisans:', error);
      if (isMounted.current) dispatch({ type: 'FETCH_FAIL' });
    }
  }, [filters]);

  // Auto‑fetch on mount and when filters change
  useEffect(() => {
    fetchArtisans();
  }, [fetchArtisans]);

  return {
    artisans: state.artisans,
    loading: state.loading,
    pagination: state.pagination,
    fetchArtisans,
  };
}