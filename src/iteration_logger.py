    def filter_log_entries(self, status: Optional[str] = None, min_iteration: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Filter log entries based on status and minimum iteration number.
        
        Args:
            status (Optional[str]): Filter entries by status (e.g., 'success', 'failure')
            min_iteration (Optional[int]): Minimum iteration number to include
        
        Returns:
            List[Dict[str, Any]]: Filtered log entries
        """
        log_entries = self.get_log_entries()
        
        filtered_entries = log_entries.copy()
        
        if status is not None:
            filtered_entries = [entry for entry in filtered_entries if entry.get('status') == status]
        
        if min_iteration is not None:
            filtered_entries = [entry for entry in filtered_entries if entry.get('iteration_number', 0) >= min_iteration]
        
        return filtered_entries