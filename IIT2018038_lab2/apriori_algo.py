import operator
from collections import defaultdict
from itertools import combinations, chain

class Apriori:
	def __init__(self, minSupport, minConfidence):
		self.support_count = defaultdict(int)
		self.minSupport = minSupport
		self.minConfidence = minConfidence

	# Read transactions from the csv file
	def readCSVFile(self, csv_file):
		with open (csv_file, 'r') as infile:
			transactions = [ set(line.rstrip('\n').split(',')) for line in infile ]
		
			return transactions

	# Gets unique items from the list of transactions
	def getOneItemset(self, transactions):
		one_itemset = set()
		for transaction in transactions:
			for item in transaction:
				one_itemset.add(frozenset([item]))
		
		return one_itemset

	# Returns those itmesets whose support is greater than minSupport
	def getMinSuppItemsets(self, Ck, transactions):
		temp_freq = defaultdict(int)

		for transaction in transactions:
			for itemset in Ck:
				if itemset.issubset(transaction):
					temp_freq[itemset] += 1
					self.support_count[itemset] += 1

		N = len(transactions)
		Lk = [ itemset for itemset, freq in temp_freq.items() if freq/N > self.minSupport ] 

		return set(Lk)

	# Takes union of a set with itself to form bigger sets
	def selfCross(self, Ck, itemset_size):
		Ck_plus_1 = {itemset1.union(itemset2) 
					for itemset1 in Ck for itemset2 in Ck 
					if len(itemset1.union(itemset2)) == itemset_size}

		return Ck_plus_1

	# Prune candidate items whose count doesnot meet minimum support
	def pruneCk(self, Ck, Lk_minus_1, itemset_size):
		Ck_ = set()
		for itemset in Ck:
			Ck_minus_1 = list(combinations(itemset, itemset_size-1))
			flag = 0
			for subset in Ck_minus_1:
				if not frozenset(subset) in Lk_minus_1:
					flag = 1
					break
			if flag == 0:
				Ck_.add(itemset)

		return Ck_

	# Uses Apriori Algorithm to find intresting k-itemsets.
	def apiori(self, transactions):
		K_itemsets = dict()
		Ck = self.getOneItemset(transactions)
		Lk = self.getMinSuppItemsets(Ck, transactions)
		k = 2
		while len(Lk) != 0:
			K_itemsets[k-1] = Lk
			Ck = self.selfCross(Lk, k)
			Ck = self.pruneCk(Ck, Lk, k)
			Lk = self.getMinSuppItemsets(Ck, transactions)
			k += 1

		return K_itemsets

	# Returns subset of a set.
	def subsets(self, iterable):
		list_ = list(iterable)
		subsets_ = chain.from_iterable(combinations(list_, len) 
				for len in range(len(list_)+1))
		subsets_ = list(map(frozenset, subsets_))
		
		return subsets_

	# Returns High Confidence rules formed from k-Itemsets.
	def getRules(self, K_itemsets):
		rules = list()
		for key, k_itemset in K_itemsets.items():
			if key > 1:
				for itemset in k_itemset:
					sub_itemsets = \
					{subset for subset in self.subsets(itemset) 
						if (subset != set() and len(subset) != len(itemset))}
					for subset in sub_itemsets:
						left = subset
						right = itemset.difference(subset)
						confidence = self.support_count[itemset]/self.support_count[left]
						if (confidence > self.minConfidence):
							rules.append((list(left), list(right), confidence))

		rules.sort(key=operator.itemgetter(2), reverse=True)
		return rules

	# Prints the Association Rules.
	def displayRules(self, rules):
		print("")
		for rule in rules:
			support_l =  self.support_count[frozenset(rule[0])]
			support_r = self.support_count[frozenset(rule[1])]
			print(str(rule[0])+'('+str(support_l)+')'+' -> '+str(rule[1])+ \
							'('+str(support_r)+')'+' | confidence: '+str(rule[2])+'\n')
		print('\nTotal number of rules: '+str(len(rules))+'\n')
		
if __name__ == '__main__':
	csv_file = "./store_data.csv"	
	minSupport = 0.02
	minConfidence = 0.55
	print("Min Support: " + str(minSupport) +"  " + "Min Confidence : " + str(minConfidence))

	ap = Apriori(minSupport, minConfidence)
	transactions = ap.readCSVFile(csv_file)
	K_itemsets = ap.apiori(transactions)
	rules = ap.getRules(K_itemsets)
	ap.displayRules(rules)