# -*- coding: utf-8 -*-
# @Author : Yupeng Hou
# @Email  : houyupeng@ruc.edu.cn
# @File   : eval_setting.py

class EvalSetting(object):
    def __init__(self, config):
        self.config = config

        self.group_field = None
        self.ordering_args = None
        self.split_args = None
        self.neg_sample_args = None

        presetting_args = ['group_field', 'ordering_args', 'split_args', 'neg_sample_args']
        for args in presetting_args:
            if config[args] is not None:
                setattr(self, args, config[args])

    def __str__(self):
        info = 'Evaluation Setting:\n'
        info += ('\tGroup by {}\n'.format(self.group_field) if self.group_field is not None else '\tNo Grouping\n')
        info += ('\tOrdering: {}\n'.format(self.ordering_args) if (self.ordering_args is not None and self.ordering_args['strategy'] != 'none') else '\tNo Ordering\n')
        info += ('\tSplitting: {}\n'.format(self.split_args) if (self.split_args is not None and self.split_args['strategy'] != 'none') else '\tNo Splitting\n')
        info += ('\tNegative Sampling: {}\n'.format(self.neg_sample_args) if (self.neg_sample_args is not None and self.neg_sample_args['strategy'] != 'none') else '\tNo Negative Sampling\n')
        return info

    def __repr__(self):
        return self.__str__()

    r"""Setting about group

    Args:
        field (str): The field of dataset grouped by, default None (Not Grouping)

    Example:
        >>> es = EvalSetting(config)
        >>> es.group_by('month')
        >>> es.group_by_user()
    """
    def group_by(self, field=None):
        self.group_field = field

    def group_by_user(self):
        self.group_field = self.config['USER_ID_FIELD']

    r"""Setting about ordering

    Args:
        strategy (str): Either 'none', 'shuffle' or 'by'
        field (str or list of str): Name or list of names
        ascending (bool or list of bool): Sort ascending vs. descending. Specify list for multiple sort orders.
            If this is a list of bools, must match the length of the field

    Example:
        >>> es = EvalSetting(config)
        >>> es.set_ordering('shuffle')
        >>> es.set_ordering('by', field='timestamp')
        >>> es.set_ordering('by', field=['timestamp', 'price'], ascending=[True, False])

    or
        >>> es = EvalSetting(config)
        >>> es.shuffle()
        >>> es.sort_by('timestamp') # ascending default
        >>> es.sort_by(field=['timestamp', 'price'], ascending=[True, False])
    """
    def set_ordering(self, strategy='none', **kwargs):
        legal_strategy = set(['none', 'shuffle', 'by'])
        if strategy not in legal_strategy:
            raise ValueError('Ordering Strategy [{}] should in {}'.format(strategy, list(legal_strategy)))
        self.ordering_args = {'strategy': strategy}
        self.ordering_args.update(kwargs)

    def shuffle(self):
        self.set_ordering('shuffle')

    def sort_by(self, field, ascending=None):
        if ascending is None:
            ascending = [True] * len(field)
            if len(ascending) == 1:
                ascending = True
        self.set_ordering('by', field=field, ascending=ascending)

    r"""Setting about split method

    Args:
        strategy (str): Either 'none', 'by_ratio', 'by_value' or 'loo'.
        ratios (list of float): Dataset will be splited into `len(ratios)` parts.
        field (str): Split by values of field.
        values (list of float or float): Dataset will be splited into `len(values) + 1` parts.
            The first part will be interactions whose field value in (*, values[0]].
        ascending (bool): Order of values after splitting.

    Example:
        >>> es = EvalSetting(config)
        >>> es.leave_one_out()
        >>> es.split_by_ratio(ratios=[0.8, 0.1, 0.1])
        >>> es.split_by_value(field='month', values=[6, 7], ascending=False)    # (*, 7], (7, 6], (6, *)

    """
    def set_splitting(self, strategy='none', **kwargs):
        legal_strategy = set(['none', 'by_ratio', 'by_value', 'loo'])
        if strategy not in legal_strategy:
            raise ValueError('Split Strategy [{}] should in {}'.format(strategy, list(legal_strategy)))
        if strategy == 'loo' and self.group_by is None:
            raise ValueError('Leave-One-Out request group firstly')
        self.split_args = {'strategy': strategy}
        self.split_args.update(kwargs)

    def leave_one_out(self):
        self.set_splitting(strategy='loo')

    def split_by_ratio(self, ratios):
        if not isinstance(ratios, list):
            raise ValueError('ratios [{}] should be list'.format(ratios))
        self.set_splitting(strategy='by_ratio', ratios=ratios)

    def split_by_value(self, field, values, ascending=True):
        if not isinstance(field, str):
            raise ValueError('field [{}] should be str'.format(field))
        if not isinstance(values, list):
            values = [values]
        values.sort(reverse=(not ascending))
        self.set_splitting(strategy='by_value', values=values, ascending=ascending)

    r"""Setting about negative sampling

    Args:
        strategy (str): Either 'none', 'to' or 'by'.
        to (int): Negative Sampling Until `pos + num == to`.
        by (int): Negative Sampling `by` neg cases for one pos case.

    Example:
        >>> es = EvalSetting(config)
        >>> es.neg_sample_to(100)
        >>> es.neg_sample_by(1)
        >>> es.full_sort()  # the same with `es.neg_sample_to(-1)`

    """
    def set_neg_sampling(self, strategy='none', **kwargs):
        legal_strategy = set(['none', 'to', 'by'])
        if strategy not in legal_strategy:
            raise ValueError('Negative Sampling Strategy [{}] should in {}'.format(strategy, list(legal_strategy)))
        self.neg_sample_args = {'strategy': strategy}
        self.neg_sample_args.update(kwargs)

    def neg_sample_to(self, to):
        self.set_neg_sampling(strategy='to', to=to)

    def full_sort(self):
        self.neg_sample_to(-1)

    def neg_sample_by(self, by):
        self.set_neg_sampling(strategy='by', by=by)