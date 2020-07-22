#include <iostream>
#include <string>
#include <typeinfo>

void compress();

void LeafIteration(const char* path){
	
	TFile* inputData = new TFile(path, "READ");
	TFile* outputData = new TFile("output.root", "RECREATE");

	TIter next(inputData->GetListOfKeys());
	TKey *key;

	//Iterate through all leaves and find those with type Float_t

	while ((key=(TKey*)next())) {
		auto tree = ((TTree*)key->ReadObj())->CloneTree();

		TObjArray* leaves = tree->GetListOfLeaves();

		size_t n = leaves->GetEntries();	
		for ( size_t i = 0; i < n; ++i){
			TLeafElement* leaf = (TLeafElement*)leaves->At(i);
			std::string type = leaf->GetTypeName();
			std::cout << type << std::endl;
			if( "Float_t" == type){
					std::cout << "Float_t leaf found in " << leaf->GetFullName() <<std::endl;

					TBranch* branch = leaf->GetBranch();

					//Create a new leaf with the compressed contents under the same branch
					//TLeafElement* compressedleaf = new TLeafElement(branch, "compressed", "Float_t");
					//
					//
					//delete leaf;
			}		
		}		

	}

	inputData->Close();

}		
